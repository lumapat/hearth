package main

import (
	"fmt"
	"os"

	"./cli/actions"

	cobra "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "hearth",
	Short: "Manage data between storage devices",
}

func main() {
	rootCmd.AddCommand(actions.NewCompareCommand())
	rootCmd.AddCommand(actions.NewListCommand())
	rootCmd.AddCommand(actions.NewSyncCommand())
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
