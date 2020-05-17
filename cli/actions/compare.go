package actions

import (
	"fmt"
	"os"
	"path/filepath"

	cobra "github.com/spf13/cobra"
)

// TODO: Add more commands to this
func NewCompareCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "compare",
		Short: "Compare the contents two or more directories",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Args: %v\n", args)
		},
	}

	return cmd
}

func getDirectoryContents(dirPath string) (map[string]bool, error) {
	var contents map[string]bool

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

type DirCompareResult struct {
	FromDirOnly []string
	ToDirOnly   []string
	BothDirs    []string
}

// TODO: Handle errors
func compareDirectories(fromDirPath string, toDirPath string) DirCompareResult {
	fromDirContents, _ := getDirectoryContents(fromDirPath)
	toDirContents, _ := getDirectoryContents(toDirPath)
	result := DirCompareResult{}

	for k := range fromDirContents {
		if !toDirContents[k] {
			result.FromDirOnly = append(result.FromDirOnly, k)
		} else {
			result.BothDirs = append(result.BothDirs, k)
		}
	}

	for k := range toDirContents {
		if !fromDirContents[k] {
			result.ToDirOnly = append(result.ToDirOnly, k)
		}
	}

	return result
}
