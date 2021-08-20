"""Input database and related classes

January 2017, C.J. Voesenek
"""
from collections import OrderedDict
import copy
from typing import Any, Dict, List, Optional, Tuple, Union

__author__ = "C.J. Voesenek"
__maintainer__ = "C.J. Voesenek"
__email__ = "cees.voesenek@wur.nl"


class InputDatabase:
    """An input database

    This class represents an input database with variables. The input
    database can be defined recursively, i.e., variables can have an
    InputDatabase as a value.

    Attributes:
        root: the root input database, this is specified if the input
            database is nested in another input database
    """

    def __init__(self, root=None) -> None:
        """Initialises an InputDatabase.

        Args:
            root: the root input database, specify this when creating nested
                input databases
        """
        self._contents = OrderedDict()  # type: OrderedDict[str, Any]
        if root is None:
            root = self
        self.root = root  # type: Optional[InputDatabase]

    def clear(self) -> None:
        """Clears the input database."""
        self._contents = OrderedDict()
        self.root = self

    def copy(self) -> "InputDatabase":
        """Creates a deep copy of the current input database.

        This is a completely new instance of the database with identical
        contents.
        """
        new = copy.deepcopy(self)
        new.set_root(new)
        return new

    def add(self, name: str, value: Any) -> None:
        """Adds a variable to the database.

        Args:
            name: Name of the variable.
            value: Value of the variable.

        Raises:
            ValueError: Variable "<name>" already exists in this database.
        """
        if name in self._contents:
            raise ValueError("Variable \"{}\" already "
                             "exists in this database.".format(name))

        self._contents[name] = value
        if type(value) is InputDatabase:
            value.set_root(self.root)

    def remove(self, name: str) -> None:
        """Removes a variable from the database.

        Args:
            name: Name of the variable to remove.

        Raises:
            ValueError: Variable "<name>" does not exist in this database.
        """
        if name not in self._contents:
            raise ValueError("Variable \"{}\" does not exist "
                             "in this database".format(name))

        del self._contents[name]

    def get(self, name: str) -> Any:
        """Retrieves a variable from the database.

        Args:
            name: Name of the variable to retrieve.

        Raises:
            ValueError: Variable "<name>" does not exist in this database.
        """
        if name not in self._contents:
            raise ValueError("Variable \"{}\" does not exist "
                             "in this database".format(name))

        return Expression.evaluate_all(self._contents[name], self)

    def set(self, name: str, value: Any) -> None:
        """Sets an existing variable from the database.

        Args:
            name: Name of the variable to set.
            value: Value to set it to.

        Raises:
            ValueError: Variable "<name>" does not exist in this database.
        """
        if name not in self._contents:
            raise ValueError("Variable \"{}\" does not exist "
                             "in this database".format(name))

        self._contents[name] = value
        if type(value) is InputDatabase:
            value.root.set_root(self.root)

    def set_root(self, root: "InputDatabase") -> None:
        """Sets the roots of this database and all its sub-databases."""

        self.root = root
        for entry in self._contents:
            if type(entry) is InputDatabase:
                # Recursively set the root database.
                self._contents[entry].set_root(self.root)

    def variables(self) -> List[str]:
        """Returns the names of variables in this database.

        Returns:
            List of variable names.
        """
        return list(self._contents.keys())

    def to_string(self, num_tab: int = 0,
                  evaluate_expressions: bool = True) -> str:
        """Convert the input database to a string.

        Args:
            num_tab: The number of tabs to prepend to each line.
            evaluate_expressions: Whether to evaluate expressions, or return
                them as strings.
        """
        val = ""
        for entry in self._contents:
            for i in range(num_tab):
                val += "\t"

            if type(self._contents[entry]) is InputDatabase:
                val += entry + " {\n"
                val += self._contents[entry].to_string(num_tab=num_tab + 1,
                                                       evaluate_expressions=
                                                       evaluate_expressions)
                for i in range(num_tab):
                    val += "\t"
                val += "}\n"
            else:
                if evaluate_expressions:
                    cur = self.get(entry)
                    if type(cur) is str:
                        val += "{} = \"{}\"\n".format(entry, cur)
                    elif type(cur) is bool:
                        val += "{} = {}\n".format(entry, str(cur).upper())
                    elif type(cur) is list:
                        all_tuple = True
                        for item in cur:
                            if type(item) is not tuple:
                                all_tuple = False
                                break
                        if all_tuple:
                            val += "{} = [{}]\n".format(entry, str(cur)[1:-1])
                        else:
                            val += "{} = {}\n".format(entry, str(cur)[1:-1])
                    else:
                        # Anything else can just be cast to a string and
                        # output immediately.
                        val += "{} = {}\n".format(entry, cur)
                else:
                    val += "{} = {}\n".format(entry, self._get_string(entry))

        return val

    def to_file(self, file: str, evaluate_expressions=False) -> None:
        """Writes the input database to a file.

        Args:
            file: Path of the file to write the input database to.
            evaluate_expressions: Whether to evaluate expressions, or return
                them as strings.
        """
        str_db = self.to_string(evaluate_expressions=evaluate_expressions)
        with open(file, "w") as f:
            f.write(str_db)

    def __contains__(self, item: str) -> bool:
        return item in self._contents

    def __str__(self) -> str:
        return self.to_string()

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __setitem__(self, key: str, value: Any) -> None:
        return self.set(key, value)

    def __iter__(self) -> Any:
        return iter(self._contents)

    def _get_string(self, name: str) -> str:
        """Retrieves an entry as a string - does not evaluate expressions.

        Args:
            name: Name of the variable to retrieve.

        Raises:
            ValueError: Variable "<name>" does not exist in this database.
        """
        if name not in self._contents:
            raise ValueError("Variable \"{}\" does not exist "
                             "in this database".format(name))

        return Expression.to_string_all(self._contents[name])

    @staticmethod
    def from_file(file: str) -> "InputDatabase":
        """Reads an input database from a file.

        Args:
            file: The file to read the input database from.

        Returns:
            The input database described in the file.
        """
        # Import here to prevent recursive import problems - we also import
        # this module in the parse module.
        from .newparser import parse

        return parse(file)


class Expression:
    """A numerical expression

    This class represents numerical expressions, optionally containing
    variables from an input database. The following operators are supported.

    Unary:
        --   negates the expression
        var  obtains the variable from the current block or the root
             database
    Binary:
        -    subtracts b from a
        +    adds b to a
        *    multiplies a and b
        /    divides a and b
        ^    takes a to the power of b

    Attributes:
        operator: The operator signifying the operation to perform.
        a: The first operand.
        b: The (optional) second operand.
    """

    def __init__(self, operator: str, a: Any, b: Any = None):
        """Initialises an expression.

        Args:
            operator: The operator signifying the operation to perform.
            a: The first operand.
            b: The (optional) second operand.
        """
        self.operator = operator  # type: str
        self.a = a  # type: Any
        self.b = b  # type: Any

    def evaluate(self, database: InputDatabase) -> float:
        """Evaluates this expression recursively.

        Args:
            database: Input database in the scope of the current expression.

        Returns:
            The numerical result of the expression.
        """
        a = Expression.evaluate_all(self.a, database)
        b = Expression.evaluate_all(self.b, database)

        if self.operator == "+":
            return a + b
        elif self.operator == "-":
            return a - b
        elif self.operator == "*":
            return a * b
        elif self.operator == "/":
            return a / b
        elif self.operator == "^":
            return a ** b
        elif self.operator == "--":
            return -a
        elif self.operator == "var":
            if a in database:
                return database.get(a)
            else:
                return database.root.get(a)

    @staticmethod
    def evaluate_all(expr: Any, database: InputDatabase) -> Any:
        """Evaluates the specified expression recursively.

        Recursively here means for any member of a list, tuple or dict. Note
        that in the case of a dict, we only evaluate the data member and not
        the key, since we don't allow keys to be expressions in the parser.

        Args:
            expr: The expression, or list or tuple of expressions to
                evaluate. Note that this may contain non-Expression objects,
                these will be returned unchanged.
            database: Input database in the scope of the current expression.

        Returns:
            The input with all expressions evaluated recursively - everything
            that was an Expression should now be a float, the rest remains
            unchanged.
        """
        if type(expr) is Expression:
            return expr.evaluate(database)
        if type(expr) is list or type(expr) is tuple:
            val = []
            for entry in expr:
                val.append(Expression.evaluate_all(entry, database))
            if type(expr) is tuple:
                val = tuple(val)
            return val
        if type(expr) is dict:
            val = dict()
            for entry in expr:
                val[entry] = Expression.evaluate_all(expr[entry], database)
            return val
        else:
            return expr

    @staticmethod
    def to_string_all(expr: Union["Expression", List, Tuple, Dict]) -> str:
        """Converts the specified expression recursively to a string.

        Args:
            expr: The expression, or list or tuple of expressions to convert.

        Returns:
            The numerical result of the expression.
        """
        if type(expr) is Expression:
            return str(expr)
        if type(expr) is list or type(expr) is tuple:
            all_tuple = True
            for item in expr:
                if type(item) is not tuple:
                    all_tuple = False
                    break
            val = ""
            if all_tuple:
                val += "["
            elif type(expr) is tuple:
                val += "("

            for entry in expr:
                val += str(Expression.to_string_all(entry)) + ", "
            val = val[:-2]

            if all_tuple:
                val += "]"
            elif type(expr) is tuple:
                val += ")"

            return val
        elif type(expr) is str:
            return "\"" + expr + "\""
        elif type(expr) is bool:
            return str(expr).upper()
        else:
            return str(expr)

    def __str__(self):
        # Convert a and b to strings - add parentheses if necessary
        if type(self.a) is Expression and \
           self.a.operator != "var" and \
           self.a.operator != "--":
            str_a = "(" + str(self.a) + ")"
        else:
            str_a = str(self.a)

        if type(self.b) is Expression and \
           self.b.operator != "var" and \
           self.b.operator != "--":
            str_b = "(" + str(self.b) + ")"
        else:
            str_b = str(self.b)

        if self.operator == "var":
            val = str_a
        elif self.operator == "--":
            val = "-" + str_a
        else:
            val = str_a + " " + self.operator + " " + str_b

        return val

    def __repr__(self):
        if self.operator == "var":
            return self.a
        elif self.operator == "--":
            return "-{}".format(str(self.a))
        else:
            return "{} {} {}".format(self.operator, str(self.a), str(self.b))
