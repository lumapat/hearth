package actions

import (
	"fmt"

	cobra "github.com/spf13/cobra"
)

func NewSyncCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "sync",
		Short: "Sync the contents two or more storage devices",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Args: %v\n", args)
		},
	}

	return cmd
}
