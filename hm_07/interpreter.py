class Interpreter:
    def __init__(self):
        self.variables = {}

    def tokenize(self, expr):
        tokens = []
        current = ''
        for ch in expr:
            if ch.isspace():  # если символ пробел
                continue
            if ch.isalnum() or ch == '.':  # если символ буква или цифра
                current += ch
            else:  # если символ операция/()
                if current:
                    tokens.append(current)  # добавляем букву/цифру/переменную
                    current = ''
                tokens.append(ch)  # добавляем операцию/()
        if current:
            tokens.append(current)
        return tokens

    def to_rpn(self, tokens):
        # алгоритм сортировочной станции Дейкстры
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        output = []
        ops = []
        for token in tokens:
            if token.isalnum() or self.is_number(token):
                output.append(token)
            elif token in precedence:
                while ops and ops[-1] != '(' and precedence.get(ops[-1], 0) >= precedence[token]:
                    output.append(ops.pop())
                ops.append(token)
            elif token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    output.append(ops.pop())
                ops.pop()  # Удалить '('
        while ops:
            output.append(ops.pop())
        return output

    def eval_rpn(self, rpn):
        stack = []
        for token in rpn:
            if self.is_number(token):
                stack.append(float(token) if '.' in token else int(token))
            elif token in self.variables:
                stack.append(self.variables[token])
            elif token in {'+', '-', '*', '/'}:
                b = stack.pop()
                a = stack.pop()
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    stack.append(a / b)
            else:
                raise ValueError(f"Unknown token: {token}")
        return stack[0]

    def is_number(self, token):
        try:
            float(token)
            return True
        except ValueError:
            return False

    def eval_expr(self, expr):
        tokens = self.tokenize(expr)
        rpn = self.to_rpn(tokens)
        return self.eval_rpn(rpn)

    def execute_line(self, line):
        line = line.strip()
        if line.startswith("input "):
            var = line[6:].strip()
            val = input(f"Input value for {var}: ")
            try:
                self.variables[var] = float(val) if '.' in val else int(val)
            except ValueError:
                raise ValueError("Number is expected")
        elif line.startswith("output "):
            expr = line[7:].strip()
            value = self.eval_expr(expr)
            print(value)
        elif '=' in line:
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()
            self.variables[var] = self.eval_expr(expr)
        elif line.startswith("#"):
            return
        else:
            raise ValueError(f"Unknown command: {line}")

    def run(self, code):
        lines = code.strip().split('\n')
        for line in lines:
            self.execute_line(line)


if __name__ == "__main__":
    code = """
    input xab
    input y
    z = (xab + y) * 2
    output z
    a = z / 3
    output a
    """
    interpreter = Interpreter()
    interpreter.run(code)
    # Input value for xab: 5
    # Input value for y: 5
    # 20
    # 6.666666666666667
