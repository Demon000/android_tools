const workerpool = require('workerpool');
const utils = require('./utils');

async function getPathsForLibraries(libraries, filesDirectory) {
	let allPaths = [];

	for (const library of libraries) {
		const paths = await utils.getPathsForLibrary(library, filesDirectory);
		allPaths = allPaths.concat(paths);
	}

	return allPaths;
}

async function filterFilesWithArch(paths, targetArch) {
	const matchingPaths = [];

	for (const path of paths) {
		const fileArch = await utils.getFileArch(path);
		if (fileArch == targetArch) {
			matchingPaths.push(path);
		}
	}

	return matchingPaths;
}

async function getNeededLibraries(path, filesDirectory) {
	const fileArch = await utils.getFileArch(path);

	const libraries = await utils.getLibraryStrings(path);

	const allPaths = await getPathsForLibraries(libraries, filesDirectory);
	const paths = await filterFilesWithArch(allPaths, fileArch);

	return paths;
}

workerpool.worker({
	getNeededLibraries
});
