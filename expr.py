import ast
import math
import operator
import random

h = 10 ** -8
N = int(math.sqrt(1 / h))
idhash = lambda s: hash(s) % (10 ** 4) 
static = lambda k: lambda x: k

const = {
	"e": math.e,
	"pi": math.pi,
}

unary = {
	"ln": math.log,
	"exp": math.exp,
	"sqrt": math.sqrt,
	"sin": math.sin,
	"cos": math.cos,
	"tan": math.tan,
	"arcsin": math.asin,
	"arccos": math.acos,
	"arctan": math.atan,
	"csc": lambda x: 1 / math.sin(x),
	"sec": lambda x: 1 / math.cos(x),
	"cot": lambda x: 1 / math.tan(x),
}

binary = {
	ast.Add: ('+', operator.add),
	ast.Sub: ('-', operator.sub),
	ast.Mult: ('*', operator.mul),
	ast.Div: ('/', operator.truediv),
	ast.Pow: ('^', math.pow),
	ast.BitXor: ('^', math.pow),
}

special = {
	"u": idhash("u"),
	"n": idhash("n"),
	"a": idhash("a"),
	"du": idhash("du"),
	"f": lambda x: x * idhash("f"),
	"g": lambda x: x * idhash("g"),
	ast.USub: lambda x: -x,
}

def parse(s):
	'Create a nested-lambda expression from a string.'
	return build_expr(ast.parse(s))

ast_hints = ast.Name, ast.Num, ast.BinOp, ast.Call, ast.UnaryOp

def build_expr(node):
	'Search for a lambdify-able AST node.'
	child = ast.iter_child_nodes(node)
	for sub in child:
		if type(sub) in ast_hints:
			return lambdify(sub)
		return build_expr(sub)
	print(ast.dump(node))
	raise Exception("Error: couldn't parse the AST.")

def lambdify(node):
	'Convert AST nodes to their lambda equivalents.'
	if isinstance(node, ast.Name):
		return lambda x: const.get(node.id, special.get(node.id, x))
	elif isinstance(node, ast.Num):
		return static(node.n)
	elif isinstance(node, ast.BinOp):
		_, fn = binary[type(node.op)]
		lfx, rfx = map(lambdify, (node.left, node.right))
		return lambda x: fn(lfx(x), rfx(x))
	elif isinstance(node, ast.Call):
		name = node.func.id
		func = unary.get(name, special.get(name))
		fx = lambdify(node.args[0])
	elif isinstance(node, ast.UnaryOp):
		func = special[type(node.op)]
		fx = lambdify(node.operand)
	return lambda x: func(fx(x))

pick_op = lambda table: random.choice(list(table.keys()))

def make_unary(child):
	op = pick_op(unary)
	fx = lambda x: unary[op](child[1](x))
	return (op, child[0]), fx

def make_binary(lhs, rhs):
	op = pick_op(binary)
	name, fn = binary[op]
	fx = lambda x: fn(lhs[1](x), rhs[1](x))
	return (name, lhs[0], rhs[0]), fx

def make_var():
	k = random.randint(2, 10)
	return "{0}x".format(k), lambda x: k * x

def func_gen(size):
	'Generate a function and its string representation given a size.'
	prob = random.random()
	if size <= 0 or prob < 0.25:
		return make_var()
	elif size <= 2 or prob < 0.50:
		return make_unary(func_gen(size - 1))
	else:
		return make_binary(func_gen(size // 2), func_gen(size // 2))

def func_infix(elt):
	if isinstance(elt, tuple):
		if elt[0] in unary:
			return elt[0] + '(' + func_infix(elt[1]) + ')'
		else:
			return ' '.join([
				func_infix(elt[1]), elt[0], func_infix(elt[2])
			])
	return elt

def equal(lhs, rhs):
	'Compare floats for equality.'
	return abs(lhs - rhs) < 0.001

domain = [0, .5, 1, 2, 5, 10, 16, math.e, math.pi]
domain.extend([-elt for elt in domain])

def check(lfx, rfx):
	'Check if two functions are equivalent.'
	def is_defined(fx, pt):
		try:
			return fx(pt)
		except:
			return False
	score, denom = 0, len(domain)
	for elt in domain:
		lhs, rhs = is_defined(lfx, elt), is_defined(rfx, elt)
		if bool(lhs) ^ bool(rhs):
			denom -= 1
		elif equal(lhs, rhs):
			score += 1
	print("Score = {0}/{1}...".format(score, denom))
	return score / denom > .5 if denom else False
	
def differentiate(fx, k):
	return (fx(k + h) - fx(k)) / h

def derivative(fx):
	return lambda x: differentiate(fx, x)

def integrate(fx, a, b):
	traps = (fx(a + (b - a) * k / N) for k in range(1, N))
	return (b - a) * (fx(a) / 2 + fx(b) / 2 + sum(traps)) / N

def integral(fx):
	return lambda x: integrate(fx, 0, x)

questions = [
	("f(x) = {0}. f'(x) = ?", derivative),
	("f(x) = {0}. f''(x) = ?", lambda fx: derivative(derivative(fx))),
	("f(x) = {0}. F(x) = ? + C", integral),
]

identities = [
	# Trig Identities
	("sin(x)^2 + cos(x)^2 = ?", static(1)),
	("cos(x)^2 = ?", parse("(1 + cos(2*x)) / 2")),
	("sin(x)^2 = ?", parse("(1 - cos(2*x)) / 2")),

	# Basic Differentiation
	("d/dx u^n = ?", parse("n * (u ^ (n - 1))")),
	("d/dx a^u = ?", parse("ln(a) * (a ^ u)")),
	("d/dx e^u = ?", parse("du * (e ^ u)")),
	("d/dx ln(u) = ?", parse("du / u")),
	# ("d/dx f(g(x)) = ?", parse("f

	# Trig Differentiation
	("d/dx sin(u) = ?", parse("du * cos(u)")),
	("d/dx cos(u) = ?", parse("du * -sin(u)")),
	("d/dx tan(u) = ?", parse("du * (sec(u) ^ 2)")),

	# Integration Formulas
	# Surface area, polar, arclen
	# ("
]

def generate():
	'Generate a word problem and its solution.'
	if random.random() < 0.33:
		return random.choice(identities)
	else:
		fstr, fx = func_gen(random.randint(1, 4))
		problem, solution = random.choice(questions)
		question = problem.format(func_infix(fstr))
		return question, solution(fx)

def repl():
	print("Calculus Blasters (REPL)")
	while True:
		prob, soln = generate()
		print("\nCalculus> " + prob)
		fx = parse(input("Blast> "))
		if check(fx, soln):
			print("Correct!")
		else:
			action = input("Incorrect. Override (y/n)? ")
			print("OK. My bad." if 'y' in action.lower() else "Moving on then...")
