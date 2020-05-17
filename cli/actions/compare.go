package actions

import (
	"container/heap"
	"fmt"
	"os"
	"path/filepath"

	cobra "github.com/spf13/cobra"
)

func NewCompareCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "compare",
		Short: "Compare the contents two or more directories",
		Args:  cobra.ExactArgs(2),
		Run: func(cmd *cobra.Command, args []string) {
			if result, err := compareDirectories(args[0], args[1]); err != nil {
				fmt.Printf("Could not compare '%s' to '%s': %s\n", args[0], args[1], err.Error())
			} else {
				fmt.Printf("Comparing '%s' to '%s' ...\n", args[0], args[1])
				result.prettyPrint()
			}
		},
	}

	return cmd
}

func getDirectoryContents(dirPath string) (map[string]bool, error) {
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

type StringHeap []string

func (h StringHeap) Len() int           { return len(h) }
func (h StringHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h StringHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *StringHeap) Push(x interface{}) {
	*h = append(*h, x.(string))
}

func (h *StringHeap) Pop() interface{} {
	old := *h
	x := old[len(old)-1]
	*h = old[0 : len(old)-1]
	return x
}

type DirCompareResult struct {
	FromDirOnly StringHeap
	ToDirOnly   StringHeap
	BothDirs    StringHeap
}

func (result *DirCompareResult) prettyPrint() {
	result.FromDirOnly.prettyPrintWithPreface("Contents from first directory")
	result.ToDirOnly.prettyPrintWithPreface("Contents from second directory")
	result.BothDirs.prettyPrintWithPreface("Contents in both directories")
}

func (h *StringHeap) prettyPrintWithPreface(preface string) {
	fmt.Println(preface)

	if h.Len() == 0 {
		fmt.Println("\tNo contents")
	} else {
		for h.Len() > 0 {
			fmt.Printf("\t%s\n", heap.Pop(h))
		}
	}

}

// TODO: Docs
func compareDirectories(fromDirPath string, toDirPath string) (DirCompareResult, error) {
	fromDirContents, fromDirError := getDirectoryContents(fromDirPath)
	if fromDirError != nil {
		return DirCompareResult{}, fromDirError
	}

	toDirContents, toDirError := getDirectoryContents(toDirPath)
	if toDirError != nil {
		return DirCompareResult{}, toDirError
	}

	result := DirCompareResult{}
	heap.Init(&result.ToDirOnly)
	heap.Init(&result.FromDirOnly)
	heap.Init(&result.BothDirs)

	for k := range fromDirContents {
		if !toDirContents[k] {
			heap.Push(&result.FromDirOnly, k)
		} else {
			heap.Push(&result.BothDirs, k)
		}
	}

	for k := range toDirContents {
		if !fromDirContents[k] {
			heap.Push(&result.ToDirOnly, k)
		}
	}

	return result, nil
}
