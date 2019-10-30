package main

import (
	"fmt"
	"pokeStore/btp"
)

type OrderTaker interface {
	TakeOrder(order *Order)
}

type Joiner interface {
	Join(*Client)
}

type Leaver interface {
	Leave(*Client)
}

type JoinerLeaver interface {
	Joiner
	Leaver
}

type Store struct {
	orders chan *Order

	join  chan *Client
	leave chan *Client

	clients map[*Client]bool
	baskets map[string]*Basket

	checkOutSystem *CheckOutSystem
}

func NewStore() *Store {
	store := &Store{
		orders:  make(chan *Order),
		join:    make(chan *Client),
		leave:   make(chan *Client),
		clients: make(map[*Client]bool),
		baskets: make(map[string]*Basket),
	}

	cs := &CheckOutSystem{}
	cs.RegisterDiscount(NewMarketingDiscountSystem(REPELENTE))
	cs.RegisterDiscount(NewCFODiscountSystem(CARAMELORARO, 19.0))
	store.checkOutSystem = cs

	return store
}

func (s *Store) CheckOut(basket Basket) float32 {
	total, totalDiscount := s.checkOutSystem.CheckOut(basket)
	return total - totalDiscount
}

func (s *Store) notifyClients(res *btp.Response) {
	for client := range s.clients {
		s.notifyClient(client, res)
	}
}

func (s *Store) notifyClient(client *Client, res *btp.Response) {
	client.responses <- res
}

func (s *Store) notifyClientWith(client *Client, code btp.StatusCode, msg string) {
	s.notifyClient(client, btp.NewResponse(code, msg))
}

func (s *Store) dispatch(order *Order) {
	req, cli := order.request, order.client
	switch req.Verb {
	case btp.Drop:
		// Remove existing basket
		basket, ok := s.baskets[req.BasketId]
		if !ok {
			msg := fmt.Sprintf("The basket '%s' does not exist", req.BasketId)
			s.notifyClientWith(cli, btp.NotFound, msg)
			return
		}
		delete(s.baskets, basket.Id)
		msg := formatMessage(cli, "dropped basket '%s'", basket.Id)
		response := btp.NewResponse(btp.NoContent, msg)
		s.notifyClients(response)
	case btp.Create:
		// Create new basket
		if basket, ok := s.baskets[req.BasketId]; ok {
			msg := fmt.Sprintf("Basket '%s' already exists", basket.Id)
			s.notifyClientWith(cli, btp.Conflict, msg)
			return
		}
		newBasket := NewBasket(req.BasketId)
		s.baskets[newBasket.Id] = newBasket
		msg := formatMessage(cli, "created basket '%s'", newBasket.Id)
		response := btp.NewResponse(btp.Created, msg)
		s.notifyClients(response)
	case btp.Add:
		// Add item to basket
		if len(s.baskets) < 1 {
			s.notifyClientWith(cli, btp.NotFound, "There are no baskets!")
		}
		basket, ok := s.baskets[req.BasketId]
		if !ok {
			msg := fmt.Sprintf("the basket '%s' does not exist", req.BasketId)
			s.notifyClientWith(cli, btp.NotFound, msg)
			return
		}
		itemType, ok := GetItemByType(req.ItemType)
		if !ok {
			msg := fmt.Sprintf("item type <%s> does not exist", req.ItemType)
			s.notifyClientWith(cli, btp.NotFound, msg)
			return
		}
		basket.AddItem(itemType, 1)
		msg := formatMessage(cli, "added a %s to basket '%s'", itemType, basket.Id)
		s.notifyClients(btp.NewResponse(btp.Ok, msg))
	case btp.Checkout:
		if len(s.baskets) < 1 {
			msg := "There are not baskets"
			response := btp.NewResponse(btp.NotFound, msg)
			s.notifyClient(cli, response)
			return
		}
		basket, ok := s.baskets[req.BasketId]
		if !ok {
			s.notifyClientWith(cli, btp.NotFound, "Basket not found")
			return
		}
		total := s.CheckOut(*basket)
		msg := formatMessage(cli, "checkout basket '%s' with a total of %g", basket.Id, total)
		s.notifyClients(btp.NewResponse(btp.Ok, msg))
	default:
		fmt.Println(fmt.Sprintf("Unknown verb %s", req.Verb))
	}
}

func (s *Store) Join(c *Client) {
	s.join <- c
}

func (s *Store) Leave(c *Client) {
	s.leave <- c
}

func (s *Store) TakeOrder (order *Order) {
	s.orders <- order
}

func (s *Store) Run() {
	for {
		select {
		case client := <-s.join:
			s.clients[client] = true
		case client := <-s.leave:
			delete(s.clients, client)
			client.Exit()
		case order := <-s.orders:
			s.dispatch(order)
		}
	}
}

func formatMessage(cli *Client, template string, args ...interface{}) string {
	msg := fmt.Sprintf("[client=%d] ", cli.Id) + fmt.Sprintf(template, args...)
	return msg
}
