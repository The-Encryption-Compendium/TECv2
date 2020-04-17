/*
 * Fuse.js config for fuzzy client-side search
 */

const default_fuse_options = {
  isCaseSensitive: false,
  findAllMatches: false,
  includeMatches: false,
  includeScore: false,
  useExtendedSearch: false,
  minMatchCharLength: 1,
  shouldSort: true,
  threshold: 0.3,
  location: 0,
  distance: 100,
  keys: ["title", "abstract", "authors"],
};

/*
 * Vue components for rendering the page
 */

const _search_stats_template = `
<div class="uk-grid-match" uk-grid>
  <div class="uk-width-1-2@m">
    <h3>Found {{ n_results }} results</h3>
  </div>
  <div class="uk-width-1-2@m uk-text-right uk-text-small">
    <span class="monospace uk-text-muted">Search finished in {{ qtime }}ms</span>
  </div>
</div>`;

const _search_result_template = `
<div class="search_result">
  <h2 class="uk-h2 uk-text-bold">{{ title }}</h2>
  <div>
    <div><span class="uk-text-bold">Authors:</span> {{ authors }}</div>
    <div><span class="uk-text-bold">Published:</span> {{ published }}</div>
    <p>
      <a v-bind:href="'/entries/' + id">See more</a>
    </p>
  </div>
  <hr>
</div>`;

Vue.component("search-stats", {
  props: ["n_results", "qtime"],
  template: _search_stats_template,
});

Vue.component("search-result", {
  props: ["title", "published", "authors", "id"],
  template: _search_result_template,
});

function generate_result_component(result) {
  /* Return a new search-result Vue component based on a search result
   * found using Fuse.js. */
  const item = result.item;
  const el = document.createElement("search-result");

  // Entry title
  el.setAttribute("title", item.title);
  el.setAttribute("published", get_publication_date(item));
  el.setAttribute("authors", get_authors(item));
  el.setAttribute("id", item.id);

  return el;
}

/*
 * Primary search function
 */
function search(pattern) {
  // Delete any child elements of the search_results DOM element and add a
  // new <search-stats></search-stats> element in its place.
  const search_stats_container = document.getElementById("search_stats");
  search_stats_container.childNodes.forEach((el) => el.remove());

  // Perform the search with Fuse
  const fuse_options = default_fuse_options;
  const fuse = new Fuse(entries, fuse_options);

  const start_time = new Date();
  const results = fuse.search(pattern);
  const end_time = new Date();

  const search_result_el = document.getElementById("search_results");

  /* Add a new element to the DOM for every search result that was
   * returned. */
  for (let ii = 0; ii < results.length; ++ii) {
    const el = generate_result_component(results[ii]);
    search_result_el.appendChild(el);
  }

  // Add search statistics
  const search_stats = document.createElement("search-stats");
  search_stats.setAttribute("n_results", results.length);
  search_stats.setAttribute("qtime", end_time.getTime() - start_time.getTime());
  search_stats_container.appendChild(search_stats);

  // Display all of the results
  new Vue({
    el: "#search_stats",
  });
  new Vue({
    el: "#search_results",
  });

  return results;
}

/*
 * Script to run on page load
 */

let query = new URLSearchParams(location.search).get("query");
if (query === null) {
  query = "";
}
search(query);

// Pre-populate the search field with the last query
document.getElementById("id_query").value = query;

// Re-run search whenever something new is put into the search bar
document.getElementById("id_query").onkeyup = function (e) {
  input = document.getElementById("id_query").value;
  console.log(input);

  // Remove all search results that are currently displayed
  document.querySelectorAll(".search_result").forEach((el) => el.remove());

  // Re-run search with new input
  search(input);
};
