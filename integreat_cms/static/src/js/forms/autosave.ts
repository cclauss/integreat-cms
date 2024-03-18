import tinymce from "tinymce";
import { getCsrfToken } from "../utils/csrf-token";

const formatDate = (date: Date) => {
    const options: Intl.DateTimeFormatOptions = {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    };

    return new Intl.DateTimeFormat(document.documentElement.lang, options).format(date);
};

export const autosaveEditor = async () => {
    const form = document.getElementById("content_form") as HTMLFormElement;
    tinymce.triggerSave();
    const formData = new FormData(form);
    // Override status to "auto save"
    formData.append("status", "AUTO_SAVE");
    // Override minor edit field to keep translation status
    formData.set("minor_edit", "on");
    // Do not create or update automatic translations on autosave
    formData.delete("automatic_translation");
    formData.delete("mt_translations_to_create");
    formData.delete("mt_translations_to_update");
    // Show auto save remark
    const autoSaveNote = document.getElementById("auto-save");
    autoSaveNote.classList.remove("hidden");
    const autoSaveTime = document.getElementById("auto-save-time");
    autoSaveTime.innerText = formatDate(new Date());
    form.addEventListener("input", () => {
        autoSaveNote.classList.add("hidden");
    });
    const data = await fetch(form.action, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken(),
        },
        body: formData,
    });
    // Set the form action to the url of the server response to make sure new pages aren't created multiple times
    form.action = data.url;

    // Mark the content as saved
    document.querySelectorAll("[data-unsaved-warning]").forEach((element) => {
        element.dispatchEvent(new Event("autosave"));
    });
};
