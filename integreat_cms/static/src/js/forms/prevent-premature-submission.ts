export default class SubmissionPrevention {
    watchedElements: HTMLElement[] = [];
    mostRecentlyClicked: HTMLElement = null;

    preventSubmission = (e: Event) => {
        e.preventDefault();
        this.mostRecentlyClicked = e.target as HTMLElement;
    };

    constructor(identifier: string) {
        const elements = document.querySelectorAll<HTMLElement>(identifier);
        elements.forEach((element) => {
            element.addEventListener("click", this.preventSubmission);
        });
        this.watchedElements = Array.from(elements);
    }

    release() {
        this.watchedElements.forEach((element) => {
            element.removeEventListener("click", this.preventSubmission);
        });
        if (this.mostRecentlyClicked !== null) {
            this.mostRecentlyClicked.click();
        }
    }
}
