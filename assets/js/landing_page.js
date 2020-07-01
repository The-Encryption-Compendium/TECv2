/*
 * Functions for tag search
 */

function toggle_tag(tag_id) {
  // Deselect the active element so that it can change color
  document.activeElement.blur();

  let tag = document.getElementById("tag-" + tag_id);
  tag.classList.toggle("deselected-tag");
  tag.classList.toggle("selected-tag");
}

function tag_search() {
  // Extract all of the tags from the "tag search" form, and then
  // search the compendium based off those tags.

  const form = document.getElementById("tag_search_form");
  const selected = form.getElementsByClassName("selected-tag");

  const tags = [];
  for (let ii = 0; ii < selected.length; ++ii) {
    const tagname = selected[ii].getAttribute("name");
    tags.push(tagname);
  }

  const url = "/search?tags=" + encodeURIComponent(JSON.stringify(tags));
  window.location.replace(url);
}
