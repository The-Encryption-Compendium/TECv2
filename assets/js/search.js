/*
 * Fuse.js config for fuzzy client-side search
 */

import { searchStatsComponent, searchResultComponent } from "./modules/components.min.js";

const default_fuse_options = {
    isCaseSensitive: false,
    findAllMatches: false,
    includeMatches: false,
    includeScore: false,
    useExtendedSearch: true,
    minMatchCharLength: 1,
    shouldSort: true,
    threshold: 0.1,
    location: 0,
    distance: 3000,
    keys: ["title", "abstract", "authors"],
};

// Create two Vue apps to display the search statistics and the search results
var searchResults = {
    results: [],
    qtime: 0,
};

/*
 * Search filters
 */

function filter_by_tags(tags, entries) {
    // Filter in only entries that have the provided tags
    if (tags.length === 0) {
        return entries;
    }

    return entries.filter((entry) =>
        tags.some((tag) => "tags" in entry && entry.tags.includes(tag))
    );
}

function filter_by_text(text, entries) {
    // Filter in only entries that match a fuzzy text search.
    // When text == "" the default behavior is to filter in every single
    // entry in the compendium.

    if (text.length === 0) {
        return entries;
    }

    const fuse = new Fuse(entries, default_fuse_options);
    const results = fuse.search(text);
    return results.map((res) => res.item);
}

function search(text, tags, entries) {
    // Filter out compendium entries based on text they contain and tags
    let results = filter_by_tags(tags, entries);
    results = filter_by_text(text, results);
    return results;
}

let query = new URLSearchParams(location.search).get("query");
if (query === null) {
    query = "";
} else {
    query = decodeURIComponent(query);
}

let tags = new URLSearchParams(location.search).get("tags");
if (tags === null) {
    tags = [];
} else {
    tags = JSON.parse(decodeURIComponent(tags));
}

/*
 * Script to run on page load
 */

fetch("/data/entries.json")
    .then(data => {
        return data.json()
    })
    .then(entries => {
        // Extract the authors and tags for each entry automatically
        entries = entries.map(e => {
            if (e.authors.length === 0) {
                e.authorString = null;
            }
            else {
                e.authorString = e.authors.join(", ");
            }
            e.tagString = e.tags.join(", ");
            return e;
        });

        // Create a new Vue app to show the search statistics and results
        const searchApp = Vue.createApp({
            components: {
                "search-stats": searchStatsComponent,
                "search-result": searchResultComponent,
            },
            data() {
                return {
                    results: searchResults.results,
                    nresults: searchResults.results.length,
                    qtime: searchResults.qtime,
                };
            },
            methods: {
                run_search() {
                    const input = document.getElementById("id_query").value;
                    const start_time = new Date();
                    const results = search(input, tags, entries);
                    const end_time = new Date();

                    this.$data.results = results;
                    this.$data.qtime = end_time.getTime() - start_time.getTime();
                    this.$data.nresults = results.length;
                }
            },
            delimiters: ["[[", "]]"],
        });

        const vm = searchApp.mount("#search-results");

        // Pre-populate the search field based on the URL parameters
        document.getElementById("id_query").value = query;

        // Run search once to populate results
        vm.run_search();
    });
