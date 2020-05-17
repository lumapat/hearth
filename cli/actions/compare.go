package actions

import (
	"fmt"

	cobra "github.com/spf13/cobra"
)

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
