// The allegories the page can tell, and the one it opens with. Written by tools/allegory.py (build, default, remove). Do not edit by hand.
const ALLEGORIES = {"default":"greece","list":[{"id":"greece","name":"Ancient Greece"},{"id":"himalaya","name":"The High Himalaya"},{"id":"venice","name":"The Venetian lagoon"}]};
// Which one this visit tells: ?allegory=<id> in the address, else the reader's last choice, else the default. Its file defines
// ALLEGORY, CITY and SIEGE, and is loaded here, before the scripts that follow, so the rest of the page finds them in place.
{
  const has = id => ALLEGORIES.list.some(a => a.id === id); let id = new URLSearchParams(location.search).get("allegory");
  if (!has(id)) { try { id = localStorage.getItem("allegory"); } catch (e) {} }
  if (!has(id)) id = ALLEGORIES.default;
  ALLEGORIES.current = id;
  document.write('<script src="allegories/' + id + '.js"></' + 'script>');
}
