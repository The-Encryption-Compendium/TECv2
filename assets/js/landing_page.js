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

/* ---- particles.js config ---- */

particlesJS("particles-js", {
  particles: {
    number: {
      value: 80,
      density: {
        enable: true,
        value_area: 800,
      },
    },
    color: {
      value: "#444",
    },
    shape: {
      type: "circle",
      stroke: {
        width: 0,
        color: "#444",
      },
      polygon: {
        nb_sides: 5,
      },
      image: {
        src: "img/github.svg",
        width: 100,
        height: 100,
      },
    },
    opacity: {
      value: 0.5,
      random: false,
      anim: {
        enable: false,
        speed: 1,
        opacity_min: 0.1,
        sync: false,
      },
    },
    size: {
      value: 3,
      random: true,
      anim: {
        enable: false,
        speed: 40,
        size_min: 0.1,
        sync: false,
      },
    },
    line_linked: {
      enable: true,
      distance: 150,
      color: "#888",
      opacity: 0.4,
      width: 1,
    },
    move: {
      enable: true,
      speed: 1,
      direction: "bottom",
      random: true,
      straight: false,
      out_mode: "out",
      bounce: false,
      attract: {
        enable: false,
        rotateX: 600,
        rotateY: 1200,
      },
    },
  },
  interactivity: {
    detect_on: "canvas",
    events: {
      onhover: {
        enable: false,
        mode: "repulse",
      },
      onclick: {
        enable: false,
        mode: "push",
      },
      resize: true,
    },
    modes: {
      grab: {
        distance: 140,
        line_linked: {
          opacity: 1,
        },
      },
      bubble: {
        distance: 400,
        size: 40,
        duration: 2,
        opacity: 8,
        speed: 3,
      },
      repulse: {
        distance: 200,
        duration: 0.4,
      },
      push: {
        particles_nb: 4,
      },
      remove: {
        particles_nb: 2,
      },
    },
  },
  retina_detect: true,
});
