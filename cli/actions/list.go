package actions

import (
	"fmt"

	"github.com/shirou/gopsutil/disk"
	cobra "github.com/spf13/cobra"
)

// Roadmap:
// Create a centralized YAML to store this (for now)
//	- Not sure if we need a more persistent store but this should be enough
// If the YAML already exists, use it
// YAML should have the following information
//	- List of hearths to keep burning!
//		- Root folder location
//		- Device name
//		- Type of storage (e.g. USB, SSD, HDD)
//
// YAML will eventually have more information, and the information may
// need to be de-centralized for better robustness. But good to defer this.

// For now, just list all the storage devices on the system!

func NewListCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "list",
		Short: "List storage devices and save points in a system",
		Run: func(cmd *cobra.Command, args []string) {
			partitions, err := disk.Partitions(false)
			if err != nil {
				fmt.Printf("Error occurred: %s\n", err.Error())
			} else {
				fmt.Println("Found the following storage devices:")
				for _, p := range partitions {
					fmt.Printf("\t%s mounted on %s\n", p.Device, p.Mountpoint)
				}
			}
		},
	}

	return cmd
}
