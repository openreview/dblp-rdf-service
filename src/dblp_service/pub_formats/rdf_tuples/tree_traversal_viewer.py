from collections import defaultdict
import typing as t

from rich.table import Table
from rich.text import Text
from rich.pretty import Pretty
from rich.console import Console
from rich.tree import Tree
from rich.style import Style

from bigtree.node.node import Node
from rich.console import ConsoleRenderable
from dblp_service.pub_formats.rdf_tuples.dblp_repr import UpdateOperation

from copy import deepcopy

from dblp_service.pub_formats.rdf_tuples.trees import get_repr, simplify_urlname  # type: ignore

P = t.ParamSpec('P')


class StepViewer:
    interactive: bool
    renderables: t.Dict[str, ConsoleRenderable]
    messages: t.List[Text]

    subj: Node
    rel: Node
    obj: Node

    def __init__(self, interactive: bool) -> None:
        self.interactive = interactive
        self.console = Console()
        self.reset()

    def reset(self):
        self.subj = Node('unset')
        self.rel = Node('unset')
        self.obj = Node('unset')
        self.renderables = defaultdict(Text)
        self.messages = []

    def scrutinees(self, subj: Node, rel: Node, obj: Node):
        self.sub = subj
        self.rel = rel
        self.obj = obj
        s = simplify_urlname(subj.node_name)
        r = simplify_urlname(rel.node_name)
        o = simplify_urlname(obj.node_name)

        message = (
            Text('Processing ')
            .append(Text(s, style='blue'))
            .append(' --[ ')
            .append(Text(r, style='green'))
            .append(' ]--> ')
            .append(Text(o, style='yellow'))
        )
        self.messages.append(message)
        self.renderables['before'] = make_rich_tree(obj)

    def handler(self, fn: t.Callable[P, t.Any]):
        message = Text('Handler function: ').append(Text.from_markup(f'[bold]{fn.__qualname__}'))

        self.messages.append(message)

    def render_messages(self):
        msgs = Table.grid()
        for msg in self.messages:
            msgs.add_row(msg)
        return msgs

    def render_before_and_after_trees(self):
        trees = Table(show_edge=False, show_footer=False)
        trees.add_column('Before', header_style='green bold')
        trees.add_column('After', header_style='green bold')
        trees.add_row(self.renderables['before'], self.renderables['after'])

        return trees

    def render_output(self):
        frame = Table(padding=1, show_edge=False)
        frame.add_row(self.render_messages())
        frame.add_row(self.render_before_and_after_trees())

        console = Console()
        console.print('')
        console.print(frame)
        self.reset()

    def ran_op(self, op: UpdateOperation):
        self.renderables['after'] = make_rich_tree(self.obj)
        message = Text('Update Operation: ').append(Text.from_markup(f'[bold blue]{str(op)}'))
        self.messages.append(message)

    def done(self):
        pass

    def msg(self, str):
        pass

    def show_tree(self, node: Node, pane: int):
        pass


def make_rich_tree(leaf: Node) -> ConsoleRenderable:
    path_to_root = [leaf, *leaf.ancestors]
    styles = [
        Style(color='red', bold=True),
        Style(color='blue', bold=True, italic=True),
        Style(color='green', bold=True),
    ]

    curr_tree: Tree = Tree('empty')
    for n, node in enumerate(path_to_root):
        if node.node_name == 'root':
            continue
        style = Style() if n > 2 else styles[n]
        rich_node = Tree(Text(node.node_name, style=style))
        if (elem := get_repr(node)) is not None:
            ecopy = deepcopy(elem)
            pretty = Pretty(ecopy, overflow='fold', max_length=120, expand_all=True)
            rich_node.add(pretty)
        if n > 0:
            rich_node.add(curr_tree)
        curr_tree = rich_node

    return curr_tree
