/**
 * Vue.js components and integration for The Encryption Compendium.
 */

const searchStatsComponent = {
    props: ["nresults", "qtime"],
    template: `\
<div class="uk-grid-match" uk-grid>
  <div class="uk-width-1-2@m">
    <h3>Found {{ nresults }} results</h3>
  </div>
  <div class="uk-width-1-2@m uk-text-right uk-text-small">
    <span class="monospace uk-text-muted">Search finished in {{ qtime }}ms</span>
  </div>
</div>`
};

const searchResultComponent = {
    props: ["title", "published", "authors", "tags", "slug"],
    template: `\
<div class="search_result">
  <h2 class="uk-h2 uk-text-bold">{{ title }}</h2>
  <div>
    <div v-if="authors !== null">
        <span class="uk-text-bold">Authors:</span> {{ authors }}
    </div>
    <div v-if="published !== null">
        <span class="uk-text-bold">Published:</span> {{ published }}
    </div>
    <div><span class="uk-text-bold">Tags:</span> {{ tags }}</div>
    <p>
      <a v-bind:href="'/entries/' + slug">See more</a>
    </p>
  </div>
  <hr>
</div>`
};

export {
    searchStatsComponent,
    searchResultComponent,
}
