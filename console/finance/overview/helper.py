# coding=utf-8

import datetime

from console.finance.tickets.helper import describe_ticket


def describe_overview_today_events(owner, ticket_status):
    resp = []

    for ticket_type in range(1, 7):
        try:
            tickets = describe_ticket(owner, ticket_type, ticket_status)
        except Exception:
            tickets = []

        resp.append(len(tickets))

    return resp


def describe_overview_tickets(owner, ticket_type, ticket_status, num):
    tickets = []
    try:
        tickets = describe_ticket(owner, ticket_type, ticket_status)
    except Exception:
        return tickets

    num = num if num > 0 else len(tickets)
    return tickets[0:num]

