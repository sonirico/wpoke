package main

import (
	"fmt"
	"log"
	"net"
	"pokeStore/cli"
)

func worker(client *Client, store *Store) {
	client.Enter(store)
	go client.Write()
	client.Read(store)
}

func main() {
	conn := cli.GetConnectionData()
	ln, err := net.Listen("tcp", conn.Url())
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		err := ln.Close()
		if err != nil {
			fmt.Println("Error when stopping the server")
		}
	}()

	store := NewStore()
	go store.Run()
	lastClientId := uint64(0)

	for {
		conn, err := ln.Accept()
		lastClientId++
		fmt.Println(fmt.Sprintf("Connected new client, Id = %d", lastClientId))
		if err != nil {
			log.Fatal(err)
		}
		client := NewClient(lastClientId, conn)
		// TODO: Implement rate limiting
		go worker(client, store)
	}
}
