from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm
from .models import Student


def landingpage(request):
    return render(request, "student/landingpage.html")


def _dashboard_context(request, add_form=None):
    """Shared context for every view that renders the student dashboard."""
    students = Student.objects.all()

    query = request.GET.get("q", "").strip()
    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(course__icontains=query)
            | Q(year_level__icontains=query)
            | Q(email__icontains=query)
            | Q(contact_number__icontains=query)
        )

    return {
        "students": students,
        "form": add_form if add_form is not None else StudentForm(),
        "query": query,
        "total_students": Student.objects.count(),
        "total_courses": Student.objects.values("course").distinct().count(),
        "total_year_levels": Student.objects.values("year_level").distinct().count(),
    }


def dashboard(request):
    # Bound to the POST data when the Add Student form is submitted.
    form = StudentForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student {student.get_full_name()} ({student.student_id}) "
                "was added successfully.",
            )
            return redirect("dashboard")

        messages.error(request, "Please fix the errors in the form and try again.")

    context = _dashboard_context(request, add_form=form)

    return render(request, "student/dashboard.html", context)


def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student, prefix="edit")

        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student {student.get_full_name()} ({student.student_id}) "
                "was updated successfully.",
            )
            return redirect("dashboard")

        messages.error(
            request, "Please fix the errors in the edit form and try again."
        )
    else:
        form = StudentForm(instance=student, prefix="edit")

    context = _dashboard_context(request)
    context["edit_form"] = form
    context["edit_student"] = student
    context["edit_modal_open"] = True

    return render(request, "student/dashboard.html", context)


def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        name = student.get_full_name()
        student.delete()
        messages.success(request, f"Student {name} was deleted.")

    return redirect("dashboard")

