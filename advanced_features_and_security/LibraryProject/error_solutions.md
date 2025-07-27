# Error Solutions Guide

## Error: No installed app with label 'bookshelf'

**Explanation:**
This error occurs when Django cannot find an app specified in your command, usually because it's not listed in `INSTALLED_APPS` in `settings.py`.

**Solution:**
1. Open your `settings.py` file.
2. Locate the `INSTALLED_APPS` list.
3. Add the app name, in this case, `'bookshelf'`, to the list like so:
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'bookshelf',
   ]
   ```
4. Save the file and re-run your command.
