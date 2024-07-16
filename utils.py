import git


def author_id_extractor(author: git.Actor):
    author_id = ""

    if author.email is None:
        author_id = author.name
    else:
        author_id = author.email

    author_id = author_id.lower().strip()
    return author_id


def iterLen(obj: iter):
    return sum(1 for _ in obj)
