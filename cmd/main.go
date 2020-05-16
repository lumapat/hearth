package main

import (
	"flag"
	"fmt"
)

type CmdlineArgs struct {
	action string
}

func (args *CmdlineArgs) initFlags() {
	flag.StringVar(&args.action, "action", "help", "hearth action to perform")
}

func main() {
	var args = CmdlineArgs{}
	args.initFlags()

	flag.Parse()
	fmt.Printf("The action you chose is %s\n", args.action)
}
