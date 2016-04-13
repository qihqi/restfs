# restfs

## About
Restfs is a simple spec to map filesystem to HTTP. For now it serves as an
simple and self contained excircise for learning new language or technology.
For now, I am learning python3's asyncio and will provide an implementation
of restfs in it.

## Spec
REST uses uri to identify resources and the 4 HTTP verbs
(GET, POST, PUT, DELETE) to represent the possible actions (fetch, update, create, delete)
on those resources. Here we will take a similar approach, and map those verbs
to actions on filesystem like read, write, append and delete. Or more specifically:

* GET /path = returns content of file in $PREFIX/path (where prefix is some predified
  chroot so we are not serving everything on / to the internet), or lists files in the
  directory if /path is a directory, or returns 404 if there is no such file.

* PUT /path = writes the body to the file in $PREFIX/path, overrides existing file,
  creates intermediate directory if not exists

* POST /path = _append_ the body of the request to the file.

* DELETE /path = deletes the file or directory

In REST, POST is used for create object, and PUT for update.
So it seems that we should use PUT for POST to create files, and PUT to append.
However, REST has chosen POST for creation because creation is an action that
may not be idempotent, i.e. calling POST /path twice will create two copies of the
give object. PUT is required to be idempotent, and updating an object twice to the
same content results the same.

In a filesystem, appending to a file is clearly the action which are not idempotent.
Therefore POST for append is the natural choice.

Giving the goal of this spec is to be as simple as possible (at least for now).
I have ignored lots of features like permissions, moving files, authorization
etc. I might add those later.
