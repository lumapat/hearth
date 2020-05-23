package actions

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// GetDirectoryContents TODO: Docs
func GetDirectoryContents(dirPath string) (map[string]bool, error) {
	contents := map[string]bool{}

	err := filepath.Walk(dirPath,
		func(path string, info os.FileInfo, err error) error {
			if err != nil {
				fmt.Println(err.Error())
			}
			contents[path] = true
			return err
		})

	return contents, err
}

type DirTree struct {
	CurDir string
	Files  []string
	Dirs   []*DirTree
}

type PathTree struct {
	CurElement string
	ChildTree  *PathTree
	IsDir      bool
}

// AddPathTree TODO: Docs
func (dt *DirTree) AddPathTree(pt *PathTree) error {
	if dt == nil || pt == nil {
		// TODO: Throw something
		return nil
	} else if dt.CurDir != pt.CurElement {
		// TODO: Throw an actual error
		return nil
	}

	if pt.IsDir {
		var foundDt *DirTree
		for _, d := range dt.Dirs {
			if d.CurDir == pt.CurElement {
				foundDt = d
				break
			}
		}

		if foundDt != nil {
			foundDt.AddPathTree(pt.ChildTree)
		} else {
			// TODO: Error check if this is good
			newDirTree := pt.ChildTree.ToDirTree()
			dt.Dirs = append(dt.Dirs, newDirTree)
		}
	} else {
		foundFile := false
		for _, f := range dt.Files {
			if f == pt.CurElement {
				foundFile = true
				break
			}
		}

		if !foundFile {
			dt.Files = append(dt.Files, pt.CurElement)
		}
	}

	return nil
}

// ToDirTree TODO: Docs
func (p *PathTree) ToDirTree() *DirTree {
	if p == nil {
		return nil
	} else if p.ChildTree == nil {
		// No directories in a file-only path
		return nil
	}

	var newDirs []*DirTree
	if p.ChildTree != nil {
		newDirs = append(newDirs, p.ChildTree.ToDirTree())
	}

	return &DirTree{CurDir: p.CurElement, Dirs: newDirs}
}

// AsPathTree TODO: Docs and error
func AsPathTree(path string) *PathTree {
	if path == "" {
		return nil
	}

	fstat, err := os.Stat(path)
	if err != nil {
		// Return an error too
		return nil
	}

	pathElements := strings.Split(path, string(filepath.Separator))
	tree := PathTree{CurElement: pathElements[0], IsDir: true}
	treeIter := &tree
	for i := 1; i < len(pathElements); i++ {
		newTree := PathTree{CurElement: pathElements[i], IsDir: true}
		tree.ChildTree = &newTree
		treeIter = &newTree
	}

	// Set last item to the result of Stat().IsDir()
	treeIter.IsDir = fstat.IsDir()

	return &tree
}

// // AsDirTree TODO: Docs
// func AsDirTree(path string) *DirTree {
// 	if path == "" {
// 		return nil
// 	}

// 	fstat, statErr := os.Stat(path)
// 	if statErr != nil {
// 		// Could not open file for stats
// 		return nil
// 	}

// 	// Only iterate up to the second to last element
// 	// as the last element can be a file
// 	pathElements := strings.Split(path, string(filepath.Separator))
// 	tree := DirTree{CurDir: pathElements[0]}
// 	treeIter := &tree
// 	for i := 1; i < len(pathElements)-1; i++ {
// 		newTree := DirTree{CurDir: pathElements[i]}
// 		treeIter.Dirs = append(treeIter.Dirs, &newTree)
// 		treeIter = &newTree
// 	}

// 	baseElement := pathElements[len(pathElements)-1]
// 	if fstat.IsDir() {
// 		treeIter.Dirs = append(treeIter.Dirs, &DirTree{CurDir: baseElement})
// 	} else {
// 		treeIter.Files = append(treeIter.Files, baseElement)
// 	}

// 	return &tree
// }

// CombineDirTrees TODO: Docs
// func CombineDirTrees(dir1 *DirTree, dir2 *DirTree) (*DirTree, error) {
// 	if dir2 == nil {
// 		return nil, fmt.Errorf("second directory is %v", dir2)
// 	} else if dir1 == nil {
// 		return nil, fmt.Errorf("first directory tree is %v", dir1)
// 	} else if dir1.CurDir != dir2.CurDir {
// 		return nil, fmt.Errorf("root directories need to match. %v (1) is not %v (2)", dir1.CurDir, dir2.CurDir)
// 	}

// 	newDir := *dir1
// 	dirSet1 := map[string]*DirTree
// 	for _, d := range iter1.Dirs {
// 		dirSet1[d.CurDir] = true
// 	}
// 	dirSet2 := map[string]*DirTree
// 	for _, d := range iter2.Dirs {
// 		dirSet2[d.CurDir] = true
// 	}

// 	fileSet

// 	for _, d := range iter2.Dirs {
// 	}
// }
