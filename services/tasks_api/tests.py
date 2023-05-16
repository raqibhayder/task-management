import uuid
from uuid import uuid4

import boto3
import pytest
from fastapi import status
from moto import mock_dynamodb
from starlette.testclient import TestClient

from main import app
from models import Task, TaskStatus
from store import TaskStore


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client: TestClient):
    """
    GIVEN a FastAPI application
    WHEN health check endpoint is called with GET method
    THEN respond with status 200 and body OK message
    """
    response = client.get("/api/health-check/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "ok"}


@pytest.fixture
def dynamodb_table():
    with mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        table_name = "test-table"
        client.create_table(
            # DynamoDB allows you to choose between two different key schemas, HASH and RANGE. The HASH key is a
            # partition key, and the RANGE key is a sort key. Together, they uniquely identify an item in the table.
            # In this case, we are using the PK and SK attributes as the HASH and RANGE keys, respectively.
            # The PK attribute is a string that represents the partition key, and the SK attribute is a string that
            # represents the sort key.
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GS1PK", "AttributeType": "S"},
                {"AttributeName": "GS1SK", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GS1',
                    'KeySchema': [
                        {
                            'AttributeName': 'GS1PK',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'GS1SK',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                },
            ],
        )
        yield table_name


def test_added_task_retrieved_by_id(dynamodb_table):
    repository = TaskStore(table_name=dynamodb_table)
    task = Task.create(id_=uuid4(), title="test", owner="test")
    repository.add(task)
    assert repository.get_by_id(task_id=task.id, owner=task.owner) == task


def test_open_tasks_listed(dynamodb_table):
    repository = TaskStore(table_name=dynamodb_table)
    open_task = Task.create(id_=uuid4(), title="test", owner="test")
    closed_task = Task(id=uuid4(), title="test", status=TaskStatus.CLOSED,  owner="test")

    repository.add(open_task)
    repository.add(closed_task)

    assert repository.list_open(owner=open_task.owner) == [open_task]


def test_closed_tasks_listed(dynamodb_table):
    repository = TaskStore(table_name=dynamodb_table)
    open_task = Task.create(uuid4(), "Clean your office", "john@doe.com")
    closed_task = Task(uuid4(), "Clean your office", TaskStatus.CLOSED, "john@doe.com")

    repository.add(open_task)
    repository.add(closed_task)

    assert repository.list_closed(owner=open_task.owner) == [closed_task]
