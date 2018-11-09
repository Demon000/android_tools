const ignoredLibraries = [
	'libbase.so',
	'libc++.so',
	'libc.so',
	'libcutils.so',
	'libdl.so',
	'libhardware_legacy.so',
	'libhidlbase.so',
	'libhidltransport.so',
	'libhwbinder.so',
	'liblog.so',
	'libm.so',
	'libprotobuf-cpp-full.so',
	'libsqlite.so',
	'libutils.so',
	'libutilscallstack.so',
	'libxml2.so',
];

module.exports = {
	isIgnoredLibrary: (library) => ignoredLibraries.includes(library),
	isImportantLibrary: (library) => !ignoredLibraries.includes(library),
};
