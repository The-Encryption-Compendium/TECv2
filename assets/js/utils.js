/*
 * Common utilities used across the site
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
 * Functions used to help display compendium entries
 */

function get_publication_date(entry) {
  // Entry publication date
  let publication_date = ""
  if ( entry.day !== null ) {
    publication_date += entry.day;
  }
  if ( entry.month !== null ) {
    publication_date += " " + month_name(entry.month);
  }
  if ( entry.year !== null ) {
    publication_date += " " + entry.year;
  }

  return publication_date;
}

function get_authors(entry) {
  // Entry authors
  if ( entry.authors.length === 0 ) {
    entry.authors = ["Unknown"];
  }
  return entry.authors.join(", ");
}
