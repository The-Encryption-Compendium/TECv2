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
 * Helper functions
 */

function month_name(month_num) {
  /* Return the name of a month corresponding to a number between
   * 1 and 12. */
  switch (month_num) {
    case 1: return "January";
    case 2: return "February";
    case 3: return "March";
    case 4: return "April";
    case 5: return "May";
    case 6: return "June";
    case 7: return "July";
    case 8: return "August";
    case 9: return "September";
    case 10: return "October";
    case 11: return "November";
    case 12: return "December";
    default: return "";
  }
}

/*
 * Vue components for rendering the page
 */

const _search_result_template = `
<div>
  <h2 class="uk-h2 uk-text-bold">{{ title }}</h2>
  <div>
    <div><span class="uk-text-bold">Authors:</span> {{ authors }}</div>
    <div><span class="uk-text-bold">Published:</span> {{ published }}</div>
  </div>
  <hr>
</div>
`

Vue.component("search-result", {
  props: ["title", "published", "authors"],
  template: _search_result_template
});

function generate_result_component(result) {
  /* Return a new search-result Vue component based on a search result
   * found using Fuse.js. */
  const item = result.item;
  const el = document.createElement("search-result");

  // Entry title
  el.setAttribute("title", item.title);

  // Entry publication date
  let publication_date = ""
  if ( item.day !== null ) {
    publication_date += item.day;
  }
  if ( item.month !== null ) {
    publication_date += " " + month_name(item.month);
  }
  if ( item.year !== null ) {
    publication_date += " " + item.year;
  }
  el.setAttribute("published", publication_date);

  // Entry authors
  if ( item.authors.length === 0 ) {
    item.authors = ["Unknown"];
  }
  el.setAttribute("authors", item.authors.join(", "));

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
