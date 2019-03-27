# Strana
Python templating engine inspired by Django's templating system

Strana is a templating engine with which it's easy to generate text files using templates.
It uses techniques inspired from Django's templating system with minor tweaks.

## Installation
Download the release tarball from the 'releases' tab and run
```
pip install strana
``` 
## Examples
```python
from Strana.context import Context
from Strana.template import Template

source = "I'm such a {= quality =} boy"

t = Template(source, None, None)
print(t.render(Context(None, {'quality': 'good'}, 'root')))

#Ouput: I'm such a good boy

```
As you can see, the {= ... =} tells the parser that whatever is inside is actually a variable.
As soon as the parser encounters this block, it searches for the variable in the context.
The context is a special wrapper around a dictionary which provides access to variables.
Here, the 'quality' variable is present inside context with a value of 'good'.

Let's try another example
```python
source = "I'm such a {= quality.0 =} boy"

t = Template(source, None, None)
print(t.render(Context(None, {'quality': ['good','bad']}, 'root')))

#Outputs: I'm such a good boy

``` 
As you can see, quality.0 is translated to quality[0].
What about dictionaries?
```python
source = "I'm such a {= quality.aniket =} boy"

t = Template(source, None, None)
print(t.render(Context(None, {'quality': {'aniket':'good'}}, 'root')))

#Output: I'm such a good boy
```
You can have simple method calls too
```python
source = "I'm such a {= quality.get =} boy"
t = Template(source, None, None)
print(t.render(Context(None, {'quality': {'get':lambda :'good'}}, 'root')))

#Output: I'm such a good boy
```

However you cannot have methods those take arguments.

Moving on,
```python
source = "I'm such a {= quality =}{# This is a comment #} boy"

t = Template(source, None, None)
print(t.render(Context(None, {'quality': 'good'}, 'root')))

#Output: I'm such a good boy
```

{# ... #} is a comment and is ignored (isn't it obvious?)

And now the most important part, actions
```python
source = """
    {> do 5 times <}
        I'm such a {= quality =} boy
    {> /do <}
"""
t = Template(source, None, None)
print(t.render(Context(None, {'quality': 'good'}, 'root')))

#Output


I'm such a good boy

I'm such a good boy

I'm such a good boy

I'm such a good boy

I'm such a good boy




```
Action tags span over more than one lines, and can modify the output, as in the example, the 
"do 5 times" tag tells the parser to repeat its body 5 times. We'll see how to write our own action

These were basic examples. In order to move to advanced, we need to have some concepts

## Concepts

### Variables
You already know what they are. They're like normal python variables and optionally can be indexable.
### Modifiers
Modifiers are optional "functions" that can access the value of a variable and modify it. They can optionally take arguments.
Suppose we have a modifer called up, which can transform a variable to uppercase, and takes an argument which
if true, will uppercase only the first letter, else will uppercase the whole value.
This is how we can use it - 
```python
source = "I'm such a {= quality>>up=>False =} boy"
 
```
The '>>' tells the parser that whatever comes next is a modifier and the => tells that the next part is an argument
We'll see how to write our own modifiers.

### Actions
We have already seen them in action (pun intended). They are basically functions which can optionally access the body, and optionally the context
and cause the output to change. We'll see how to write our own actions soon.

### Library
This class is responsible for acting as a collection of modifiers and actions. You can write your own modifiers and actions and register them
with a library and pass the library to the template.

### Engine
They are optional helper classes which facilitate template loading and error printing.
You can specify a path to the engine, a string to be shown for errors, and a library. Next time, you can just pass in the name of template file to the engine,
and it will load it with the proper library.

### Node
Think of nodes as boxes, where some data is stored. When parsing, each variable, comment and action
is converted to a node. Each node has an id. When rendering, the render method of these nodes is called which returns the output for the corresponding
node. You can write your own node, although that's probably not necessary.

###
This is a wrapper over a dict. Other than providing access to variables, it does some thing which we'll see soon.
### Template
This is the heart of the system. This class is basically a collection of parsed nodes.
You pass the context and it gives the output. The same templates can be rendered with different contexts.

## Advanced Usages
### Using an engine

In most of the cases, using the DefaultEngine class is enough. This class provides you with
provided you with two basic builtin tags - the "for i in x" and "do i times" tag.
**You should use this class only to provide the template path.** For your own libraries, pass them to the template.


```python
from Strana.engine import DefaultEngine
from Strana.template import Template
en = DefaultEngine('templates')
source = "{> do 2 times <}HI{>/do}"

```
Now use the **load_templates** method of the engine to load a template.
The template **should have an extension of '.ptm'**. If it's something else pass the whole name

```python
t=Template(en.load_template('xyz'),en,None) #Will load templates/xyz.ptm
t=Template(en.load_template('xyz.abc'),en,None) #Will load templates/xyz.abc

```
### Using a library and writing own actions

Before starting writing an action, let's take a look at different types of actions

* **Basic action:** They're simple, take no argument, are only one line, can save their output in the context, and do really simple jobs
(e.g. Printing the time)
* **Loop action:** These actions span over multiple lines, can access whatever is inside them, and require a closing tag.
* **Pattern tag:** These tags can match custom patterns, say for example, "Show me your marks" or "do n times"

Now let's see each of them in action.

First import the library class and create an instance
```python
from Strana.library import Library
r = Library()
```
Now to register a basic action, use the basic_action() function.

**Every action must take node_id as first argument.**
```python
@r.basic_action(name='time',need_context=False)
#name: defines the name of the block
#need_context: If true, the context will be passed to the function and it must accept it as the second argument
def fun(node_id):# Every action must take the node ID as the first argument
    return str(datetime.now()) # Return a string.

source = "{> time <} Test"
t = Template(source,None,[r]) # [r]= list of libraries, you can pass as many libraries as you want
print(t.render(Context(None,{},'root')))

#Output: 2017-12-11 15:15:47.266049
```
You can save the output using the 'as' keyword and use it later
```python
source = "{> time as t <} Hi {= t =}"
#The 'as' keyword stores the output in the variable t
...

#Output: Hi 2017-12-11 15:15:47.266049
```

For registering a loop action, you'll use the loop_action method. 
This method must be given a name, which will identify the name of the action
For example, a basic if action - 

```python
@r.loop_action(name='if',need_context=True)
#need_context: If True, the action will be passed the context
def fun(node_id,body,context,cond):
#Loop actions will be passed the body and the 2nd function must be named body.
#If need_context is True, the 3rd argument must be named context
#Any additional arguments will came after.

#body is just a list of nodes which can be rendered
    if cond:
        return ''.join([str(node.render(context)) for node in body])
    else:
        return ''
source = """
    {> if True <}
        Hi
    {> /if <}
"""
#Output:
Hi
```

As you can see, the arguments to the action are space separated. Moreover, an ending tag is required.
The ending tag is just / followed by the name.

Now, time for a pattern action.

To register a pattern action, you'll use the pattern_action method. This method requires a name argument
just like others, a need_context argument, and a need_body argument if you want access to the body.
Additionally, a pattern argument is required. The patterns can be any string. You'll use <> for arguments.
During runtime, the pattern will be mathced, and whatever mathces in place of <> will be passed as strings.

Say your pattern is "do <> times". Remember, the pattern must start with whatever was passed to the name argument.

Now, you write {> do 8 times <}.

When the parser encounters this line, it calls the action with "8" as argument. Note
that it's passed as a string. It's upto the function to change it to proper type.

If need_context is True, the context is passed and the 3rd argument must be named context.

If need_body is True, an ending tag is required, and the 2nd argument must be body.

Here is the code of "do n times" pattern. It makes a variable named "iteration"
which holds the value of current iteration and exists only in this block.
```python
@r.pattern_action(name='do', pattern='do <> times', need_body=True, need_context=True)
def do_action(node_id, body, context, times):
#times is whatever matches with <>
    result = ''
    try:
        times = int(times)
        for i in range(times):
            c = context.push_temporary({'iteration': i}, node_id)
            result += ''.join([str(node.render(c)) for node in body])
    except ValueError:
        pass
    return result
```

### Writing modifiers

To write a modifier, we'll use the register_modifier method. This method also takes the name argument
and a function. The first argument to this function must be the value which is to be modified.
Any additional argument follows this.

Here's the code of the up modifier
```python
@r.register_modifier(name='up')
def up(value, first_letter=False):
    return value.title() if first_letter else value.upper()
```
When you call it like this

```python
{= some_var>>up =}
```
The value of some_var is passed as the first argument.

To supply the first_letter argument, you'll write this - 
```python
{= some_var>>up=>True =}
```

### Builtin Library

The builtin library provides two useful action for you.

One is the "do n times" stated abov, and another is the "for i in l" action,
which is exactly what you expect it to be.

## Using Context

Context class provides a helpful wrapper over a dict for managing variables. (I
have said that twice already). To initiate a context, you'll need to first import the class.
```python
from Strana.context import Context
```

Then pass an engine, a dict which holds the variables, and a node id.
This node id can be any string. Generally for the starting Context, we use 'root'.

```python
ctx = Context(None,{'Hi':'Hello'},'root')
```

If you print ctx, you'll see this - 

```python
Context bound to node root: OrderedDict([('builtin', {'True': True, 'False': False, 'None': None}), ('root', {'Hi': 'Hello'})])
```

Note the 'builtin' part. Those three are provided for you. Isn't that cute?

Also, note that the context is bound to node 'root'. Whenever a node adds some new variables, it has to bind itself to the context.
Don't worry, it happens automatically.

There are only two methods that you should use at this point - 

* push_temporary
* push_permanent

push_temporary returns a copy of current context with some new variables added. This is useful if you want some variables 
only within a block.

Remember the "do n times" action? Of course you don't. Here's the code.
```python
@r.pattern_action(name='do', pattern='do <> times', need_body=True, need_context=True)
def do_action(node_id, body, context, times):
    result = ''
    try:
        times = int(times)
        for i in range(times):
            #We push the new values temporarily
            #A new copy of the context is returned
            c = context.push_temporary({'iteration': i}, node_id)
            result += ''.join([str(node.render(c)) for node in body])
    except ValueError:
        pass
    return result
```
For a closer look let's see this - 
```python
ctx = Context(None,{'Hi':'Hello'},'root')
print(ctx)
with ctx.push_temporary({'test':'Wow'},'some_node') as c:
    print(c)

#Output
Context bound to node root: OrderedDict([('builtin', {'True': True, 'False': False, 'None': None}), ('root', {'Hi': 'Hello'})])
Context bound to node some_node: OrderedDict([('builtin', {'True': True, 'False': False, 'None': None}), ('root', {'Hi': 'Hello'}), ('some_node', {'test': 'Wow'})])
```

push_permanent pushes a dict which persists till the end.

Context class also provides a pop_last method which pops the last node to which it was bound.
It should not be used by the user (and it has no practical use too at this point).

## Author
* **Aniket Bhattacharyea**
## License
This project is licensed under GNU General Public License v3

## Acknowledgments
* [Django project](https://djangoproject.com)
