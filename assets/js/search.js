/*
 * Fuse.js config for fuzzy client-side search
 */
const fuse_options = {
  isCaseSensitive: false,
  findAllMatches: false,
  includeMatches: false,
  includeScore: false,
  useExtendedSearch: false,
  minMatchCharLength: 1,
  shouldSort: true,
  threshold: 0.6,
  location: 0,
  distance: 100,
  keys: [
    "title",
    "abstract",
    "authors",
  ]
};

const fuse = new Fuse(entries, fuse_options);

/*
 * Vue components for rendering the page
 */

const _search_result_template = `
<div>
  <h2 class="uk-h2 uk-text-bold">{{ title }}</h2>
  <div>
    <div><span class="uk-text-bold">Authors:</span> {{ authors }}</div>
    <div><span class="uk-text-bold">Published:</span> {{ published }}</div>
    <p>
      <a v-bind:href="'/entries/?id=' + entry_id">See more</a>
    </p>
  </div>
  <hr>
</div>
`;

Vue.component("search-result", {
  props: ["title", "published", "authors", "entry_id"],
  template: _search_result_template
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

  return el;
}

/*
 * Primary search function
 */
function search(pattern) {
  const start_time = new Date();
  const results = fuse.search(pattern);
  const end_time = new Date();

  const search_result_el = document.getElementById("search_results");

  /* Add a new element to the DOM for every search result that was
   * returned. */
  for ( let ii = 0; ii < results.length; ++ii ) {
    const el = generate_result_component(results[ii]);
    el.setAttribute("entry_id", ii);
    search_result_el.appendChild(el);
  }

  /* Display all of the results */
  new Vue({
    el: "#search_results",
    delimiters: ["[[", "]]"],
    data: {
      n_results: results.length,
      qtime: end_time.getTime() - start_time.getTime(),
    }
  });
  
  return results;
}

const query = new URLSearchParams(location.search).get("query");
if ( query !== null ) {
  search(query);
}
else {
  search("");
}
