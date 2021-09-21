/*
 * Client-side research assistant for The Encryption Compendium
 */

/**
 * Class representing the user's research profile. This profile is stored entirely
 * client-side and contains notes, markup, tags, and so on that the user has created
 * while navigating the compendium.
 */
class UserProfile {
    constructor() {
        this.custom_tags = [];
        this.annotations = new Map();
    }

    /**
     * Export the profile to a JSON file that the user can download.
     * @param {string} filename - The filename that the profile should be downloaded with.
     */
    export(filename) {
        // Use Blob API to convert the profile into a data stream that may be downloaded
        // by the user.
        const data = new Blob([JSON.stringify(this, null, 2)], {type: "application/json"});
        const url = URL.createObjectURL(data);

        // Create a temporary link node that we will click on to start the download
        let download_node = document.createElement("a");
        download_node.style.display = "none";
        download_node.href = url;
        download_node.download = filename;
        document.body.appendChild(download_node);

        download_node.click();

        // Now that we've clicked the node and initiated the download process, we no longer
        // need the node.
        download_node.remove();
    }

    /**
     * Import the profile from a JSON file uploaded by the user.
     */
    import() {
        return this;
    }
}

// Create a single global user profile, which serves as the current profile that is being used
const globalProfile = new UserProfile();

/**
 * Retrieve the current global user profile.
 * @return {UserProfile} The global user profile.
 */
function getCurrentUserProfile() {
    return globalProfile;
}

export {
    UserProfile,
}
