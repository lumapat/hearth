package actions

import (
	"fmt"

	cobra "github.com/spf13/cobra"
)

func NewListCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "list",
		Short: "List storage devices and save points in a system",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Args: %v\n", args)
		},
	}

	return cmd
}
