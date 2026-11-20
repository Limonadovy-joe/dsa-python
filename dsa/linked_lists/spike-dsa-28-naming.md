# Spike DSA-28: naming of value/callback params and returned nodes

Two questions come from TODOs in `linked_list.py`:

1. What should we call a parameter that takes a value *or* a callback?
   Today that is `find(value_or_callback: T | Callable[[T], bool])`.
2. What should `delete`, `delete_head`, `delete_tail` and `find` return: the
   node, the value, or both?

## Q1: value-or-callback parameter → split it into two methods

### Problems with `T | Callable[[T], bool]`

- **It's ambiguous at runtime.** `callable(x)` picks the branch. So a
  `LinkedList[Callable[..., Any]]`, such as a list of handlers, can never be
  searched by value. The function you pass in gets *called* as if it were a
  predicate. `Queue.find(item)` (`dsa/queues/queue.py`) inherits the same bug.
- **It's weak for typing.** mypy can't narrow an unbounded `T` against
  `Callable`, so every call site has to accept a union.
- **No good name fits.** `value_or_callback` just spells out the union, which
  is a sign the parameter does two jobs.

### Prior art

| Source | API |
|---|---|
| trekhleb/javascript-algorithms (the origin of this code) | `find({ value, callback })` |
| C++ STL | `std::find(value)` / `std::find_if(predicate)` |
| Python stdlib | `Callable[[T], bool]` is called a `predicate` (`itertools.takewhile`, `filterfalse`); a key extractor is `key` (`sorted`, `min`, `max`) |

### Decision

- `find(value: T) -> Node | None` compares with the list's comparator.
- `find_if(predicate: Callable[[T], bool]) -> Node | None` returns the first
  node whose value satisfies the predicate.
- Callbacks are named after their **role**, never `cb` or `callback`:

| Signature | Name |
|---|---|
| `Callable[[T], bool]` | `predicate` |
| `Callable[[T], K]` (ordering) | `key` |
| `Callable[[T], str]` | `stringifier` (already used in queues and deques) |
| `Callable[[T, T], int]` | `compare_fun` (already used; the type is owned by DSA-27) |

## Q2: returned nodes → return the node, `None` on a miss

### Options

- **Return the value** (like `list.pop`). This is ambiguous: `T` may include
  `None`, so "not found" and "found a stored `None`" look the same.
- **Raise on a miss** (like `list.remove` / `ValueError`). This is Pythonic, but
  it changes every caller and test, and a miss on a search is not exceptional.
- **Return `Node | None`** (current behaviour). This is unambiguous. Nodes are
  public (`LinkedListNode` and `DoublyLinkedListNode` are in `__all__`), so the
  caller can work on the node in O(1).

### Decision: keep `Node | None`, and make the contract explicit

- **Removal** (`delete`, `delete_head`, `delete_tail`) returns the **detached**
  node. Its `next` and `previous` are cleared. It returns `None` if nothing
  matched or the list is empty.
- **Lookup** (`find`, `find_if`) returns the **live** node, still linked into
  the list.
- **ADT wrappers** (`Queue`, `Deque`) return **values** and never expose nodes.
  They already unwrap `.value`.
- **Local variables** are named after their role: `removed` and `found`, not
  `node_to_return`.

## Follow-up (applied under DSA-28)

- Split `LinkedList.find` into `find` / `find_if`, and add the same pair to
  `DoublyLinkedList`.
- Rename `node_to_return` → `removed`.
- Rename `DoublyLinkedList.to_array(cb)` and `LinkedListNode.to_string(callback)`
  → `stringifier`.
- Add tests: a callable value is found by `find` without being called, `find`
  returns a live node, and `delete` returns a detached node.
- Copy the rules into `docs/conventions.md`.
