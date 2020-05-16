package main

import (
	"flag"
	"fmt"
)

type CmdlineArgs struct {
	action string
}

func (args *CmdlineArgs) initFlags() {
	flag.StringVar(&args.action, "a", "nil", "hearth action to perform (list|sync|compare)")
}

func main() {
	var args = CmdlineArgs{}
	args.initFlags()

	flag.Parse()
	switch args.action {
	case "compare":
		fmt.Printf("'%s' to be implemented", args.action)
	case "list":
		fmt.Printf("'%s' to be implemented", args.action)
	case "sync":
		fmt.Printf("'%s' to be implemented", args.action)
	default:
		fmt.Printf("Nothing can be done for action '%s'\n", args.action)
	}
}
