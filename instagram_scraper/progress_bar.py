import os
import sys


class ProgressBar:

    def __init__(self, total_count, show_count):
        self.__total_count = total_count
        self.__current_count = 0
        self.__show_count = show_count

        self.update(0)

    def update(self, update_count):
        """ Receives an update increment to print the progress bar """

        if self.__total_count == 0:
            return

        self.__current_count += update_count

        if self.__current_count > self.__total_count:
            percentage = 100
        else:
            percentage = int(self.__current_count / self.__total_count * 100)

        if self.__show_count:
            status = str(self.__current_count) + ' / ' + str(self.__total_count)
        else:
            status = ''

        dots_bar_total = 75
        dots = int(dots_bar_total / 100 * percentage)
        space = dots_bar_total - dots
        bar = '['
        for _ in range(dots):
            bar += '.'
        for _ in range(space):
            bar += ' '
        bar += ']'

        # For visualization in terminal
        if len(str(percentage)) == 1:
            # 0% - 9%
            sys.stdout.write('\r' + ' ' + str(percentage) + '%   ' + bar + ' ' + status)
        elif len(str(percentage)) == 2:
            # 10% - 99%
            sys.stdout.write('\r' + ' ' + str(percentage) + '%  ' + bar + ' ' + status)
        else:
            # 100%
            sys.stdout.write('\r' + ' ' + str(percentage) + '% ' + bar + ' ' + status)

    def close(self):
        sys.stdout.write('\n')
