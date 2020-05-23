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

// DirTree TODO: Docs
type DirTree struct {
	CurDir string
	Files  map[string]bool
	Dirs   map[string]*DirTree
}

// PathTree TODO: Docs
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
		// Always start with the same root elements
		// and this will never be hit in the recursive calls
		// TODO: Throw an actual error
		return nil
	} else if pt.ChildTree == nil {
		// TODO: ERROR?!
		return nil
	}

	childElement := pt.ChildTree.CurElement
	if pt.ChildTree.IsDir {
		childDt := dt.Dirs[childElement]
		if childDt == nil {
			// TODO: Handle nil
			dt.Dirs[childElement] = pt.ChildTree.ToDirTree()
		} else {
			// TODO: Handle error
			childDt.AddPathTree(pt.ChildTree)
		}
	} else {
		if !dt.Files[childElement] {
			dt.Files[childElement] = true
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

	newDirTree := DirTree{CurDir: p.CurElement}
	if p.ChildTree != nil {
		if p.ChildTree.IsDir {
			newDirTree.Dirs[p.ChildTree.CurElement] = p.ChildTree.ToDirTree()
		} else {
			newDirTree.Files[p.ChildTree.CurElement] = true
		}
	}

	return &newDirTree
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
		newElement := tree.CurElement + string(filepath.Separator) + pathElements[i]
		newTree := PathTree{CurElement: newElement, IsDir: true}
		tree.ChildTree = &newTree
		treeIter = &newTree
	}

	// Set last item to the result of Stat().IsDir()
	treeIter.IsDir = fstat.IsDir()

	return &tree
}

// CompDir TODO: Docs and import heap
type CompDir struct {
	DirOne []string
	DirTwo []string
	Both   []string
}

// CompareDirTrees TODO: Docs
func CompareDirTrees(dt1 *DirTree, dt2 *DirTree) *CompDir {
	if dt1 == nil || dt2 == nil {
		return nil
	}
	return nil
}
