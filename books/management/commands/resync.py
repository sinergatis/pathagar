import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from books import models
from books.storage import LinkableFile

from addepub import get_epubs_paths


class Command(BaseCommand):
    help = ("Update the database files information, replacing the pointers "
            "to the original files and the symbolic links to match the "
            "specified items if the database contains a Book that is "
            "considered a duplicate (having the same sha256 hash).")

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('item', nargs='+', type=unicode,
                            help=("A file with '.epub' extension or a "
                                  "directory (in which case it is traversed "
                                  "recursively, checking all the files with "
                                  "'.epub' extension)."))

        # Named (optional) arguments
        parser.add_argument(
            '--replace-strategy', '-r',
            choices=['original', 'always-link', 'always-copy'],
            dest='replace_strategy',
            default='original',
            help=('Select the strategy to use when replacing. Allowed '
                  'values: "always-link" (always replace the file with'
                  ' a symlink), "always-copy" (always use a copy of '
                  'the file), "original" (default, use the same as '
                  'the original Book is using).')
        )

    def handle(self, *args, **options):
        epub_filenames = get_epubs_paths(options['item'])

        if not epub_filenames:
            raise CommandError('No .epub files found on the specified paths.')

        for filename in epub_filenames:
            book, success = (None, False)
            try:
                book, success = self.process_epub(filename,
                                                  options['replace_strategy'])
            except Exception as e:
                print 'Unhandled exception while processing: %s' % e

            if book:
                if success:
                    print 'Book #%s (%s) modified (%s).' % (book.pk, book,
                                                            book.original_path)
                else:
                    print 'Book #%s (%s) NOT modified.' % (book.pk, book)
            else:
                print 'No match found.'

    def process_epub(self, filename, replace_strategy='original'):
        """Parse a single EPUB from `filename`, updating `Book` if `filename`
        already exists on the database:
            - the `original_path` is updated to point to `filename`.
            - if `book_file` is a symlink, the old symlink is deleted and a new
            one pointing at `filename` is created.

        Returns a tuple (Book, success), where Book will be None if not found.
        """
        # TODO: move prints to logging.
        print '\nReimporting %s' % filename

        # Check the sha256sum and try to find the Book.
        file_sha256sum = models.sha256_sum(File(open(filename)))
        try:
            book = models.Book.objects.get(file_sha256sum=file_sha256sum)
        except models.Book.DoesNotExist:
            return (None, False)

        # Prepare the changes.
        info_dict = {'original_path': filename}
        if replace_strategy == 'always-link':
            # Remove previous file/link and create a new link.
            book.book_file.delete()
            info_dict['book_file'] = LinkableFile(open(filename))
            pass
        elif replace_strategy == 'always-copy':
            # Remove previous file only if it was a link, create a new *copy*.
            if os.path.islink(os.path.join(settings.MEDIA_ROOT,
                                           book.book_file.path)):
                book.book_file.delete()
                info_dict['book_file'] = File(open(filename))
        else:  # 'default'
            # Remove previous file only if it was a link, create a new *link*..
            if os.path.islink(os.path.join(settings.MEDIA_ROOT,
                                           book.book_file.path)):
                book.book_file.delete()
                info_dict['book_file'] = LinkableFile(open(filename))

        # Save and return the Book.
        # TODO: if save fails, files might have been deleted and leave the
        # model in inconsistent state - it's probably a better idea to delete
        # files *after* a successful book.save().
        try:
            if 'book_file' in info_dict:
                book.book_file.save(os.path.basename(filename),
                                    info_dict['book_file'],
                                    save=False)
                print 'book saved at %s' % book.book_file
            book.original_path = info_dict['original_path']
            book.save()

            return book, True
        except Exception as e:
            # TODO: check for possible risen exceptions at a finer grain.
            raise e

        return book, False
