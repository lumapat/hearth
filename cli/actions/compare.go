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

type stringHeap []string

func (h stringHeap) Len() int           { return len(h) }
func (h stringHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h stringHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *stringHeap) Push(x interface{}) {
	*h = append(*h, x.(string))
}

func (h *stringHeap) Pop() interface{} {
	old := *h
	x := old[len(old)-1]
	*h = old[0 : len(old)-1]
	return x
}

type dirCompareResult struct {
	fromDirOnly stringHeap
	toDirOnly   stringHeap
	bothDirs    stringHeap
}

func (result *dirCompareResult) prettyPrint() {
	result.fromDirOnly.prettyPrintWithPreface("Contents from first directory")
	result.toDirOnly.prettyPrintWithPreface("Contents from second directory")
	result.bothDirs.prettyPrintWithPreface("Contents in both directories")
}

func (h *stringHeap) prettyPrintWithPreface(preface string) {
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
func compareDirectories(fromDirPath string, toDirPath string) (dirCompareResult, error) {
	fromDirContents, fromDirError := getDirectoryContents(fromDirPath)
	if fromDirError != nil {
		return dirCompareResult{}, fromDirError
	}

	toDirContents, toDirError := getDirectoryContents(toDirPath)
	if toDirError != nil {
		return dirCompareResult{}, toDirError
	}

	result := dirCompareResult{}
	heap.Init(&result.toDirOnly)
	heap.Init(&result.fromDirOnly)
	heap.Init(&result.bothDirs)

	for k := range fromDirContents {
		if !toDirContents[k] {
			heap.Push(&result.fromDirOnly, k)
		} else {
			heap.Push(&result.bothDirs, k)
		}
	}

	for k := range toDirContents {
		if !fromDirContents[k] {
			heap.Push(&result.toDirOnly, k)
		}
	}

	return result, nil
}
