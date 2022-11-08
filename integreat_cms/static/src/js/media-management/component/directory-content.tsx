/*
 * This component renders a grid of all subdirectories and all files of the current directory
 */
import { Link } from "preact-router";
import { StateUpdater, useState } from "preact/hooks";

import { MediaLibraryEntry, File, Directory } from "..";
import DirectoryEntry from "./directory-entry";
import FileEntry from "./file-entry";

export interface DraggedElement {
    type: "file" | "directory";
    id: number;
}

interface Props {
    fileIndexState: [number | null, StateUpdater<number | null>];
    mediaLibraryContent: MediaLibraryEntry[];
    mediaTranslations: any;
    globalEdit?: boolean;
    allowDrop: boolean;
    setDraggedItem: (item: DraggedElement) => unknown;
    dropItem: (directoryId: number) => unknown;
}

export default function DirectoryContent({
    fileIndexState,
    mediaLibraryContent,
    mediaTranslations,
    globalEdit,
    setDraggedItem,
    dropItem,
    allowDrop,
}: Props) {
    // The file index contains the index of the file which is currently opened in the sidebar
    const [fileIndex, setFileIndex] = fileIndexState;

    return (
        <div className="grid grid-cols-gallery max-h-full gap-1">
            {mediaLibraryContent.map((entry: MediaLibraryEntry, index: number) =>
                entry.type === "directory" ? (
                    <Link href={`/${entry.id}/`} media-library-link>
                        <DirectoryEntry
                            directory={entry as Directory}
                            mediaTranslations={mediaTranslations}
                            globalEdit={globalEdit}
                            allowDrop={(!(entry as Directory).isGlobal || globalEdit) && allowDrop}
                            itemDropped={() => dropItem(entry.id)}
                            dragStart={() => setDraggedItem({ type: "directory", id: entry.id })}
                            dragEnd={() => setDraggedItem(null)}
                        />
                    </Link>
                ) : (
                    <FileEntry
                        file={entry as File}
                        active={index === fileIndex}
                        onClick={(e) => {
                            e.stopPropagation();
                            setFileIndex(index);
                        }}
                        mediaTranslations={mediaTranslations}
                        globalEdit={globalEdit}
                        dragStart={() => setDraggedItem({ type: "file", id: entry.id })}
                        dragEnd={() => setDraggedItem(null)}
                    />
                )
            )}
        </div>
    );
}