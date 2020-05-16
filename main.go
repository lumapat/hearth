package main

import (
	"fmt"
	"os"

	cobra "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "hearth",
	Short: "Manage data between storage devices",
}

var compareCmd = &cobra.Command{
	Use:   "compare",
	Short: "Compare the contents two or more directories",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("Args: %v\n", args)
	},
}

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List storage devices and save points in a system",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("Args: %v\n", args)
	},
}

var syncCmd = &cobra.Command{
	Use:   "sync",
	Short: "Sync the contents two or more storage devices",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("Args: %v\n", args)
	},
}

func main() {
	rootCmd.AddCommand(compareCmd)
	rootCmd.AddCommand(listCmd)
	rootCmd.AddCommand(syncCmd)
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
