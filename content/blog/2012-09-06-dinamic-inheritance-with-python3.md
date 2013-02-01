Title: Dynamic inheritance with python3
Tags: python, python3, metaprogramming

I've been experimenting in my spare time with metaclasses in python3 and I had an idea (for possible use). I need an instance of an object inherits from several mixins, but I will not declare the class.

When you need many combinations of these mixins, you have to create a class for each combination of inheritance you need. If many mixins, this can be tedious, and in some cases unnecessary.

Doing this dynamically (at the time of creating the instance), is the solution to this "problem".

Example:

<script src="https://gist.github.com/3654502.js?file=dinamic_inheritance.py"></script>
