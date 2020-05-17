package actions

import (
	"fmt"

	cobra "github.com/spf13/cobra"
)

// TODO: Implement a sync
//
// Might need to share the code from Compare
// but this command will need to sync files based on a
// list of strategies
//	- TrueMasterCopy (Highest priority ID)
//		- Delete data not found in MasterCopy
//		- Add only new data found only in MasterCopy
//	- NewFilesOnly
//		- Add only new data found in any copy across all copies
//  - AddByMasterCopy
//		- Add only new data found only in MasterCopy
//		- Keep data existing in other copies
//  - TrimByMasterCopy
//		- Delete data not found in MasterCopy
//		- Do not add other data

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
