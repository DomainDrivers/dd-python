# Notes about Python localization of DD

## Code

In most cases, classes are rewritten 1 to 1, keeping the same naming.

This is to make it easy to navigate through code when some names appear in video materials.

Another benefit is to make maintenance easier. Should any changes be made to Java version, they can be then easily applied to Python version as well.

Some classes that had only static methods were turned into a bunch of functions in a module, e.g. `SlotToNormalizedSlot`.

Names of files, methods, arguments and test names was mostly translated 1 to 1, adjusting to naming conventions. Java people use `camelCase`, while Pythonistas go with `snake_case`.

File names were transalted automatically using `inflection` library, with a few manually corrected exceptions.

## Dataclasses

Python version uses [dataclasses](https://docs.python.org/3/library/dataclasses.html) heavily. Whenever it was possible, `frozen=True` was used to provide faux-immutability.

## Typing

A project of such a scale wouldn't be maintainable without type hints, so they were introduced right from the start and verified using `mypy --strict`.

On a few very rare occassions one had to resort to `# type: ignore` comments. They were necessary for python-mockito and factory_boy libraries (both are untyped) and configuration of dependency injection for abstract types.

## Null references, Optional and null object pattern

In Java version on several occassions `null` was passed or returned in place of an object, e.g. in code to be implemented as a task. This wouldn't pass `mypy` checks, so instead exceptions were raised like `NotImplementedError` or Null Object Pattern was introduced in several places.

For example, there is a class `Owner` that has a field of type `uuid`. In Java, when there was no `Owner`, null was used. In Python, a null object pattern is used with a special value `UUID(int=0)` to denote lack of owner. That value is later persistend in the database and used in comparisons inside `Owner` class. It doesn't affect the code in any other way thanks to the elegance of the original design and nicely built abstractions.

Java version uses [Optional](https://www.baeldung.com/java-optional) type to indicate that a given action might or might return a result. In Python version, although such constructs also exist in 3rd party libraries, it was completely omitted and union of a return type and None was used. `mypy` then forces us to handle both situations (lack of result and presence of such), so the effect is the same.

### Generics

Since Java version uses Generics heavily in one place, the same solution was translated into Python using new generics syntax and (yet) incomplete checks implemented in mypy.

## Dependency injection

Java version uses Spring Boot which is essentially a large dependency injection container. In the original version of the code, so-called autowiring is used heavily in both 'production' and test code.

Python version relies as well on dependency injection and the container chosen is [Lagom](https://lagom-di.readthedocs.io/en/latest/).

Lagom is also used in tests, only wrapped by pytest's fixture system (which, BTW, is another example of IoC).

## Database models

Java version uses JPA standard to translate objects of almost arbitrary Java classes into database rows. In Java, some fields are translated into JSONB rows, others are 'nested'. Example of the latter are IDs, which are wrapped UUID and in database, they are put in a single column of UUID type.

To get similar behaviour, a bit of glue code was written to translate Python dataclasses in both directions. The solution uses sqlalchemy's [TypeDecorators](https://docs.sqlalchemy.org/en/20/core/custom_types.html#sqlalchemy.types.TypeDecorator) and [declarative mapping compatible with dataclasses](https://docs.sqlalchemy.org/en/20/orm/dataclasses.html) to achieve a result that is both very similar and pythonic at the same time.

Logic of adapting classes to JSONB and reversed is powered by Pydantic's [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/) and generic classes.

The implementation is located in `smartschedule/shared/sqlalchemy_extensions.py`.

## Repositories

In Java version repositories are provided by Jakarta library. In Python version, repository has been added manually, wrapping sqlalchemy's `Session` to provide very similar interface to Java's counterpart, implementing only needed methods.

The amount of added code is minimal, yet with a power of generic classes, the solution is quite elegant and universal.

## Database queries

Whenever possible, using raw SQL queries was omitted because they could be very easily written using SqlAlchemy.

Not 100% of raw queries were replaced with Python code, though.

## Transactions

The original Java version uses [@Transactional](https://docs.spring.io/spring-framework/reference/data-access/transaction.html) annotation to denote boundaries of database transactions.

This aspect was omitted in Python version. Usually, transaction is handled manually on a higher level than application service (e.g. in view or middleware), so it wasn't included.


One can quite easily imagine though how would that work - either manually using sqlalchemy's Session with context manager & commit in transactional method OR write a custom decorator that would be doing the same.

```python
with session.begin():
    # execute logic, do some DB operations
    # commits transaction at the end, or rolls back if there was an exception raised
```

