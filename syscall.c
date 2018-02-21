#include "userprog/syscall.h"
#include <stdio.h>
#include <syscall-nr.h>
#include "threads/interrupt.h"
#include "threads/thread.h"
#include "threads/synch.h"
#include "process.h"
#include "threads/vaddr.h"
#include "pagedir.h"
#include "process.h"


static void syscall_handler (struct intr_frame *);

void
syscall_init (void)
{
  intr_register_int (0x30, 3, INTR_ON, syscall_handler, "syscall");
}

int validator (const void *p)
{
  if (is_user_vaddr (p))
    if (pagedir_get_page (thread_current ()->pagedir, p))
      return 1;
  return 0;
}

static void
syscall_handler (struct intr_frame *f)
{
  lock_acquire (&sys_lock);
  struct sys_proc *p = thread_current ()->th_proc;
  lock_release (&sys_lock);
  if (validator ((const void*) f->esp) == 0)
  {
    lock_acquire (&sys_lock);
    p->exit_status = -1;
    f->eax = -1;
    lock_release (&sys_lock);
    thread_exit ();
  }
  else
{
  int sys_num = *(int*) f->esp; // Номер системного вызова
  int *sys_args = (int*) f->esp + 1; // Аргументы системного вызова

  if (sys_num == SYS_EXIT)
  {
    p->exit_status = sys_args[0];
    int i = 0;
    while (i < 255)
    {
      if (validator (p->files[i]) == 1)
        file_close (p->files[i]);
      ++i;
    }
    thread_exit ();
    return;
  }

  if (sys_num == SYS_HALT)
  {
    shutdown ();
    return;
  }

  if (sys_num == SYS_EXEC)
  {
    if (validator (sys_args[0]) == 1)
      f->eax = process_execute (sys_args[0]);
    else
      f->eax = -1;
    return;
  }

  if (sys_num == SYS_WAIT)
  {
    if (is_user_vaddr (sys_args[0]))
    {
    f->eax = process_wait (sys_args[0]);
    return;
    }
    else
    {
      f->eax = -1;
      return;
    }
  }

  if (sys_num == SYS_CREATE)
  {
    if (validator (sys_args[0]) == 1)
      f->eax = filesys_create (sys_args[0], sys_args[1]);
    else
    {
      lock_acquire (&sys_lock);
      f->eax = -1;
      p->exit_status = -1;
      lock_release (&sys_lock);
      thread_exit ();
    }
    return;
  }

  if (sys_num == SYS_REMOVE)
  {
    if (validator (sys_args[0]) == 1)
      f->eax = filesys_remove (sys_args[0]);
    else
      f->eax = -1;
    return;
  }

  if (sys_num == SYS_OPEN)
  {
    if (validator (sys_args[0]) == 1)
    {
      struct file *files = filesys_open (sys_args[0]);
      static int fd = 1;
      if (!files)
      {
        f->eax = -1;
        return;
      }
      fd++;
      lock_acquire (&sys_lock);
      p->files[fd] = files;
      lock_release (&sys_lock);
      f->eax = fd;
    }
    else
    {
      lock_acquire (&sys_lock);
      f->eax = -1;
      p->exit_status = -1;
      lock_release (&sys_lock);
      thread_exit ();
    }
    return;
  }

  if (sys_num == SYS_CLOSE)
  {
    lock_acquire (&sys_lock);
    if ((validator (sys_args[0]) == 1) && (sys_args[0] > 1) && (sys_args[0] < 256))
    {
      int fd = sys_args[0];
      if (p->files[fd])
        file_close (p->files[fd]);
      lock_release (&sys_lock);
      return;
    }
    f->eax = -1;
    lock_release (&sys_lock);
    return;
  }

  if (sys_num == SYS_FILESIZE)
  {
    lock_acquire (&sys_lock);
    if ((is_user_vaddr (sys_args[0])) && (sys_args[0] > 1) && (sys_args[0] < 256))
    {
      int fd = sys_args[0];
      if (p->files[fd])
      {
        f->eax = file_length (p->files[fd]);
        lock_release (&sys_lock);
        return;
      }
    }
    f->eax = -1;
    lock_release (&sys_lock);
    return;
  }

  if (sys_num == SYS_READ)
  {
    lock_acquire (&sys_lock);
    if ((sys_args[0] < 0) || (sys_args[0] == 1) || (sys_args[0] >= 256))
    {
      f->eax = -1;
      lock_release (&sys_lock);
      return;
    }
    if (validator (sys_args[1]) == 0)
    {
      p->exit_status = -1;
      lock_release (&sys_lock);
      thread_exit ();
      return;
    }
    int fd = sys_args[0];
    unsigned int filesize = sys_args[2];
    char *buffer = sys_args[1];
    if (fd == 0)
    {
      int i = 0;
      while (i < filesize)
      {
        buffer[i] = input_getc ();
        ++i;
      }
      f->eax = i;
      lock_release (&sys_lock);
      return;
    }
    if (p->files[fd] == NULL)
    {
      f->eax = -1;
      lock_release (&sys_lock);
      return;
    }
    f->eax = file_read (p->files[fd], buffer, filesize);
    lock_release (&sys_lock);
    return;
  }

  if (sys_num == SYS_WRITE)
  {
    lock_acquire (&sys_lock);
    if ((sys_args[0] < 1) || (sys_args[0] >= 256))
    {
      f->eax = -1;
      lock_release (&sys_lock);
      return;
    }
    if (validator (sys_args[1]) == 0)
    {
      p->exit_status = -1;
      lock_release (&sys_lock);
      thread_exit ();
      return;
    }
    unsigned int filesize = sys_args[2];
    char *buffer = sys_args[1];
    if (sys_args[0] == 1)
    {
      putbuf (buffer, filesize);
      f->eax = filesize;
      lock_release (&sys_lock);
      return;
    }
    if (p->files[sys_args[0]] == NULL)
    {
      f->eax = -1;
      lock_release (&sys_lock);
      return;
    }
    f->eax = file_write (p->files[sys_args[0]], buffer, filesize);
    lock_release (&sys_lock);
    return;
  }

}
}
