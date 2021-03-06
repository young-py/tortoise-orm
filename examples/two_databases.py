"""
This example demonstrates how you can use Tortoise if you have to
separate databases

Disclaimer: Although it allows to use two databases, you can't
use relations between two databases

Key notes of this example is using db_route for Tortoise init
and explicitly declaring model apps in class Meta
"""
import asyncio
from sqlite3 import OperationalError

from tortoise import Tortoise, fields
from tortoise.backends.sqlite.client import SqliteClient
from tortoise.models import Model
from tortoise.utils import generate_schema


class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name

    class Meta:
        app = 'tournaments'


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    tournament_id = fields.IntField()
    # Here we make link to events.Team, not models.Team
    participants = fields.ManyToManyField(
        'events.Team', related_name='events', through='event_team'
    )

    def __str__(self):
        return self.name

    class Meta:
        app = 'events'


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name

    class Meta:
        app = 'events'


async def run():
    client = SqliteClient('example_2db_first.sqlite3')
    second_client = SqliteClient('example_2db_second.sqlite3')
    await client.create_connection()
    await second_client.create_connection()
    Tortoise.init(db_routing={
        'tournaments': client,
        'events': second_client,
    })
    await generate_schema(client)
    await generate_schema(second_client)

    tournament = await Tournament.create(name='Tournament')
    await Event(name='Event', tournament_id=tournament.id).save()

    try:
        await client.execute_query('SELECT * FROM "event"')
    except OperationalError:
        print('Expected it to fail')
    results = await second_client.execute_query('SELECT * FROM "event"')
    print(results)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
