#!/usr/bin/env python3
"""Check locally linked images in app/index.html (and the stylesheets/scripts it loads),
upload new or changed images to Cloudflare R2 via Wrangler, and rewrite links in the page
to serve them from the specified custom domain.

Usage:
  python3 tools/offload_images.py images.detangled.dev
  python3 tools/offload_images.py --domain images.detangled.dev --bucket daag2
  python3 tools/offload_images.py images.detangled.dev --dry-run
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_HTML = os.path.join(REPO, "app", "index.html")
DEFAULT_BUCKET = "daag2"
CACHE_PATH = os.path.join(HERE, ".r2-upload.cache")

IMG_EXT = r"(?:webp|png|jpe?g|gif|avif|svg)"
MIME_TYPES = {
    ".webp": "image/webp",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".avif": "image/avif",
    ".svg": "image/svg+xml",
}

LOCAL_IMG_RE = re.compile(
    rf"(?<![A-Za-z0-9_/:.-])(?:\.\./|\./)?(img/[A-Za-z0-9_./-]+\.{IMG_EXT})(?![A-Za-z0-9_.-])"
)
REMOTE_IMG_RE = re.compile(
    rf"https?://([A-Za-z0-9.-]+)/(img/[A-Za-z0-9_./-]+\.{IMG_EXT})(?![A-Za-z0-9_.-])"
)
TMPL_IMG_RE = re.compile(
    rf"(?:https?://([A-Za-z0-9.-]+)/)?(?:\./)?(img/[^`\"'\s]*\$\{{([A-Za-z_][A-Za-z0-9_]*)\}}[^`\"'\s]*\.{IMG_EXT})"
)


def normalize_domain(raw: str) -> str:
    """Normalize a domain or URL down to its bare host[:port] name."""
    domain = raw.strip()
    domain = re.sub(r"^https?://", "", domain, flags=re.IGNORECASE)
    domain = domain.split("/", 1)[0].strip()
    if not domain or not re.fullmatch(r"[A-Za-z0-9.-]+(?::\d+)?", domain):
        sys.exit(f"error: invalid domain {raw!r}")
    return domain


def find_wrangler_cmd() -> tuple[list[str], dict[str, str]]:
    """Locate wrangler (or npx) and build an environment with Node on PATH for cron/non-login use."""
    env = os.environ.copy()
    extra_bins: list[str] = []
    nvm_bins = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin")), reverse=True)
    extra_bins.extend(nvm_bins)
    extra_bins.extend(["/opt/homebrew/bin", "/usr/local/bin"])

    current_path = env.get("PATH", "")
    path_parts = [p for p in current_path.split(os.pathsep) if p]
    for b in extra_bins:
        if os.path.isdir(b) and b not in path_parts:
            path_parts.append(b)
    env["PATH"] = os.pathsep.join(path_parts)

    wrangler = shutil.which("wrangler", path=env["PATH"])
    if wrangler:
        return [wrangler], env
    npx = shutil.which("npx", path=env["PATH"])
    if npx:
        return [npx, "wrangler"], env
    sys.exit("error: neither 'wrangler' nor 'npx' was found on PATH or in ~/.nvm")


def discover_page_files(html_path: str) -> list[str]:
    """Return index.html and all local stylesheets, scripts, and allegory data files it loads."""
    html_path = os.path.abspath(html_path)
    if not os.path.isfile(html_path):
        sys.exit(f"error: HTML file not found: {html_path}")
    app_dir = os.path.dirname(html_path)
    html = open(html_path, encoding="utf-8").read()
    html_no_comments = re.sub(r"<!--.*?-->", "", html, flags=re.S)

    files = [html_path]
    seen = {html_path}

    def add_local(rel: str) -> None:
        if not rel or re.match(r"^(?:https?:)?//|^data:", rel, re.IGNORECASE):
            return
        rel_clean = rel.split("?", 1)[0].split("#", 1)[0]
        full = os.path.normpath(os.path.join(app_dir, rel_clean))
        if os.path.isfile(full) and full not in seen:
            seen.add(full)
            files.append(full)

    for m in re.finditer(r"""<(?:link|script)\b[^>]*?\b(?:href|src)\s*=\s*["']([^"']+)["']""", html_no_comments, re.I):
        add_local(m.group(1))

    allegories_js = os.path.join(app_dir, "js", "data", "allegories.js")
    if allegories_js in seen:
        src = open(allegories_js, encoding="utf-8").read()
        m = re.search(r"const\s+ALLEGORIES\s*=\s*(\{.*?\});", src, re.S)
        if m:
            try:
                data = json.loads(m.group(1))
                for item in data.get("list", []):
                    if isinstance(item, dict) and item.get("id"):
                        add_local(os.path.join("allegories", f"{item['id']}.js"))
            except json.JSONDecodeError:
                pass

    allegories_dir = os.path.join(app_dir, "allegories")
    if os.path.isdir(allegories_dir):
        for name in sorted(os.listdir(allegories_dir)):
            if name.endswith(".js"):
                add_local(os.path.join("allegories", name))

    return files


def expand_template_images(text: str, tmpl_path: str, var_name: str, app_dir: str) -> list[str]:
    """Expand JS template literal image paths like img/${file}-800.webp using helper call sites."""
    keys: set[str] = set()
    # Match helper functions whose parameter list includes var_name, e.g. const skin = (file, ...) => ...
    fn_re = re.compile(rf"(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\(\s*{re.escape(var_name)}\b")
    for fn_match in fn_re.finditer(text):
        fn_name = fn_match.group(1)
        for call in re.finditer(rf"\b{re.escape(fn_name)}\s*\(\s*[\"']([^\"']+)[\"']", text):
            keys.add(call.group(1))

    out: list[str] = []
    if keys:
        for val in sorted(keys):
            rel = tmpl_path.replace("${" + var_name + "}", val)
            if os.path.isfile(os.path.join(app_dir, rel)):
                out.append(rel)
        return out

    # Fallback: match files on disk matching the template wildcard
    pattern = os.path.join(app_dir, tmpl_path.replace("${" + var_name + "}", "*"))
    for full in sorted(glob.glob(pattern)):
        if os.path.isfile(full):
            out.append(os.path.relpath(full, app_dir).replace(os.sep, "/"))
    return out


def collect_images(files: list[str], app_dir: str) -> tuple[set[str], dict[str, tuple[str, str]]]:
    """Scan page files for local and previously offloaded image keys.

    Returns:
      local_keys: image keys currently referenced as local relative paths
      all_keys: map of r2_key -> (local_abs_path, current_text_kind) for every referenced image
    """
    local_keys: set[str] = set()
    all_keys: dict[str, str] = {}

    def record(key: str, is_local: bool) -> None:
        full = os.path.normpath(os.path.join(app_dir, key))
        if os.path.isfile(full):
            all_keys[key] = full
            if is_local:
                local_keys.add(key)

    for path in files:
        text = open(path, encoding="utf-8").read()
        for m in LOCAL_IMG_RE.finditer(text):
            record(m.group(1), is_local=True)
        for m in REMOTE_IMG_RE.finditer(text):
            record(m.group(2), is_local=False)
        for m in TMPL_IMG_RE.finditer(text):
            host, tmpl_rel, var_name = m.group(1), m.group(2), m.group(3)
            for expanded in expand_template_images(text, tmpl_rel, var_name, app_dir):
                record(expanded, is_local=(host is None))

    return local_keys, all_keys


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_cache(path: str) -> dict[str, str]:
    if not os.path.isfile(path):
        return {}
    try:
        data = json.load(open(path, encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_cache(path: str, cache: dict[str, str]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def upload_object(
    wrangler_cmd: list[str],
    env: dict[str, str],
    bucket: str,
    key: str,
    local_path: str,
) -> tuple[str, str]:
    ext = os.path.splitext(local_path)[1].lower()
    ctype = MIME_TYPES.get(ext, "application/octet-stream")
    cmd = [
        *wrangler_cmd,
        "r2",
        "object",
        "put",
        f"{bucket}/{key}",
        "--file",
        local_path,
        "--content-type",
        ctype,
        "--cache-control",
        "public, max-age=31536000",
        "--remote",
    ]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        detail = (res.stderr or res.stdout).strip()
        raise RuntimeError(f"failed uploading {key} to {bucket}: {detail}")
    return key, ctype


def rewrite_file_links(text: str, domain: str, valid_keys: set[str]) -> str:
    """Rewrite local img/... paths and existing offloaded URLs to https://<domain>/img/...."""
    base = f"https://{domain}"

    def sub_tmpl(m: re.Match[str]) -> str:
        tmpl_rel = m.group(2)
        return f"{base}/{tmpl_rel}"

    def sub_remote(m: re.Match[str]) -> str:
        key = m.group(2)
        return f"{base}/{key}" if key in valid_keys else m.group(0)

    def sub_local(m: re.Match[str]) -> str:
        key = m.group(1)
        return f"{base}/{key}" if key in valid_keys else m.group(0)

    text = TMPL_IMG_RE.sub(sub_tmpl, text)
    text = REMOTE_IMG_RE.sub(sub_remote, text)
    text = LOCAL_IMG_RE.sub(sub_local, text)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Upload locally linked images from app/index.html to Cloudflare R2 and rewrite links."
    )
    parser.add_argument("domain_pos", nargs="?", help="Public domain serving the R2 bucket (e.g. images.detangled.dev)")
    parser.add_argument("-d", "--domain", dest="domain_opt", help="Public domain serving the R2 bucket")
    parser.add_argument("-b", "--bucket", default=DEFAULT_BUCKET, help=f"R2 bucket name (default: {DEFAULT_BUCKET})")
    parser.add_argument("--html", default=DEFAULT_HTML, help="Path to index.html (default: app/index.html)")
    parser.add_argument("--workers", type=int, default=4, help="Parallel upload workers (default: 4)")
    parser.add_argument("--force", action="store_true", help="Re-upload all referenced images even if cached")
    parser.add_argument("--dry-run", action="store_true", help="Report planned uploads and link updates without writing")
    args = parser.parse_args(argv)

    if args.domain_pos and args.domain_opt and normalize_domain(args.domain_pos) != normalize_domain(args.domain_opt):
        parser.error("positional domain and --domain do not match")
    raw_domain = args.domain_opt or args.domain_pos
    if not raw_domain:
        parser.error("a target domain is required (e.g. python3 tools/offload_images.py images.detangled.dev)")

    domain = normalize_domain(raw_domain)
    html_path = os.path.abspath(args.html)
    app_dir = os.path.dirname(html_path)

    page_files = discover_page_files(html_path)
    local_keys, all_keys = collect_images(page_files, app_dir)
    if not all_keys:
        print("no linked images found")
        return 0

    cache = load_cache(CACHE_PATH)
    to_upload: list[tuple[str, str, str]] = []
    for key in sorted(all_keys):
        local_path = all_keys[key]
        digest = sha256_file(local_path)
        cache_key = f"{args.bucket}:{key}"
        if args.force or key in local_keys or cache.get(cache_key) != digest:
            to_upload.append((key, local_path, digest))

    print(
        f"scanned {len(page_files)} page files; found {len(all_keys)} image(s) "
        f"({len(local_keys)} local link(s), {len(to_upload)} to upload to r2://{args.bucket})"
    )

    if to_upload:
        if args.dry_run:
            for key, local_path, _ in to_upload:
                print(f"  [dry-run] upload {os.path.relpath(local_path, REPO)} -> {args.bucket}/{key}")
        else:
            wrangler_cmd, env = find_wrangler_cmd()
            with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
                futures = {
                    pool.submit(upload_object, wrangler_cmd, env, args.bucket, key, local_path): (key, digest)
                    for key, local_path, digest in to_upload
                }
                for fut in as_completed(futures):
                    key, digest = futures[fut]
                    _, ctype = fut.result()
                    cache[f"{args.bucket}:{key}"] = digest
                    print(f"  uploaded {key} ({ctype})")
            save_cache(CACHE_PATH, cache)

    valid_keys = set(all_keys)
    updated_files: list[str] = []
    for path in page_files:
        orig = open(path, encoding="utf-8").read()
        rewritten = rewrite_file_links(orig, domain, valid_keys)
        if rewritten != orig:
            updated_files.append(path)
            if not args.dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(rewritten)

    for path in updated_files:
        prefix = "[dry-run] update" if args.dry_run else "updated"
        print(f"  {prefix} {os.path.relpath(path, REPO)}")
    if not updated_files:
        print("page links already up to date")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
