import os
import logging

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    View,
)
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy

from flashcards.models import Flashcard
from flashcards.forms import FlashcardForm
from flashcards.services.renderers import (
    RendererFactory,
    TextRenderer,
    FlashcardStandard,
)
from flashcards.services.flashcard_facade import FlashcardFacade
from flashcards.services.group_service import GroupService
from flashcards.services.learning_service import LearningService
from flashcards.services.ocr import OCRProcessor

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Mixins for Reusability
# ------------------------------------------------------------------
class CategoryContextMixin:
    """
    Mixin to add categories to the context.
    """

    def get_categories(self):
        return GroupService.get_categories()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = self.get_categories()
        return context


class FlashcardSuccessMessageMixin:
    """
    Mixin to add success messages after form submissions.
    """

    success_message = ""

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


# ------------------------------------------------------------------
# 1) LIST FLASHCARDS
# ------------------------------------------------------------------
class FlashcardListView(TemplateView):
    """
    Displays flashcards grouped by categories with pagination.
    Shows 5 categories per page and 5 flashcards per category per page.
    """

    template_name = "flashcards/flashcard_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve all categories
        categories = GroupService.get_categories()

        # Paginate categories: 5 per page
        paginator_categories = Paginator(categories, 5)  # 5 categories per page
        page_number_categories = self.request.GET.get("page_categories", 1)
        page_obj_categories = paginator_categories.get_page(page_number_categories)

        # For each category in the current page, paginate flashcards: 5 per category per page
        flashcards_by_category = {}
        paginator_by_category = {}

        for category in page_obj_categories.object_list:
            flashcards = GroupService.get_flashcards_by_category(category).order_by(
                "id"
            )
            paginator_flashcards = Paginator(
                flashcards, 5
            )  # 5 flashcards per category per page
            page_number_flashcards = self.request.GET.get(
                f"page_flashcards_{category}", 1
            )
            page_obj_flashcards = paginator_flashcards.get_page(page_number_flashcards)

            flashcards_by_category[category] = page_obj_flashcards.object_list
            paginator_by_category[category] = page_obj_flashcards

        context.update(
            {
                "page_obj_categories": page_obj_categories,
                "flashcards_by_category": flashcards_by_category,
                "paginator_by_category": paginator_by_category,
            }
        )
        return context


# ------------------------------------------------------------------
# 2) ADD FLASHCARD
# ------------------------------------------------------------------
class AddFlashcardView(CategoryContextMixin, FlashcardSuccessMessageMixin, CreateView):
    """
    View to handle adding a new flashcard.
    """

    model = Flashcard
    form_class = FlashcardForm
    template_name = "flashcards/add_flashcard.html"
    success_url = reverse_lazy("flashcards:flashcard_list")
    success_message = "Flashcard has been successfully added."


# ------------------------------------------------------------------
# 3) EDIT FLASHCARD
# ------------------------------------------------------------------
class EditFlashcardView(CategoryContextMixin, FlashcardSuccessMessageMixin, UpdateView):
    """
    View to handle editing an existing flashcard.
    """

    model = Flashcard
    form_class = FlashcardForm
    template_name = "flashcards/edit_flashcard.html"
    success_url = reverse_lazy("flashcards:flashcard_list")
    success_message = "Flashcard updated successfully."


# ------------------------------------------------------------------
# 4) DELETE FLASHCARD
# ------------------------------------------------------------------
class DeleteFlashcardView(DeleteView):
    """
    View to handle the deletion of a flashcard.
    """

    model = Flashcard
    template_name = "flashcards/confirm_delete.html"
    success_url = reverse_lazy("flashcards:flashcard_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Flashcard deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ------------------------------------------------------------------
# 5) DISPLAY FLASHCARD (TEXT or HTML)
# ------------------------------------------------------------------
class DisplayFlashcardView(DetailView):
    """
    View to display a single flashcard in text format with an option to play audio.
    """

    model = Flashcard
    template_name = "flashcards/display_flashcard.html"
    context_object_name = "flashcard"

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: render flashcard as text and provide audio URL if requested.
        """
        self.object = self.get_object()
        render_format = self.request.GET.get("format", "text").lower()
        language = self.request.GET.get("lang", "en").lower()

        # Validate language selection
        if language not in ["en", "pl"]:
            language = "en"  # Default to English if unsupported language is provided

        # Initialize renderer based on format
        if render_format == "audio":
            # Prepare audio URL for embedding
            audio_url = reverse(
                "flashcards:flashcard_audio",
                kwargs={"pk": self.object.pk, "lang": language},
            )
            # Initialize text renderer for displaying text alongside audio
            renderer = RendererFactory.get_renderer("text")
            flashcard_standard = FlashcardStandard(self.object, renderer, language)
            rendered_content = flashcard_standard.display()

            context = self.get_context_data(object=self.object)
            context.update(
                {
                    "rendered_content": rendered_content,
                    "render_format": render_format,
                    "selected_language": language,
                    "audio_url": audio_url,
                }
            )
            return self.render_to_response(context)
        else:
            # For text format, render the template with context
            renderer = RendererFactory.get_renderer("text")
            flashcard_standard = FlashcardStandard(self.object, renderer, language)
            rendered_content = flashcard_standard.display()

            context = self.get_context_data(object=self.object)
            context.update(
                {
                    "rendered_content": rendered_content,
                    "render_format": render_format,
                    "selected_language": language,
                }
            )
            return self.render_to_response(context)


class FlashcardAudioView(View):
    """
    View to serve audio files for flashcards.
    """

    def get(self, request, pk, lang):
        """
        Handle GET requests to serve the audio file.
        """
        # Retrieve the flashcard or return 404
        flashcard = get_object_or_404(Flashcard, pk=pk)

        # Validate language; default to English if unsupported
        if lang not in ["en", "pl"]:
            lang = "en"

        try:
            renderer = RendererFactory.get_renderer("audio")
            audio_data = renderer.render(flashcard, language=lang)
        except ValueError:
            # Fallback to English if renderer fails
            renderer = RendererFactory.get_renderer("audio")
            audio_data = renderer.render(flashcard, language="en")

        # Serve the audio file
        return HttpResponse(audio_data, content_type="audio/mpeg")


# ------------------------------------------------------------------
# 6) LEARNING MODE
# ------------------------------------------------------------------
class LearnFlashcardsView(TemplateView):
    """
    Learning mode for a specific category.
    """

    template_name = "flashcards/learn_flashcard.html"

    def get(self, request, *args, **kwargs):
        category = self.kwargs.get("category")
        flashcards = GroupService.get_flashcards_by_category(category)

        if not flashcards.exists():
            messages.warning(
                request, f"No flashcards available in category '{category}'."
            )
            return redirect("flashcards:flashcard_list")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get("category")
        flashcards = GroupService.get_flashcards_by_category(category)

        flashcard = LearningService.get_next_flashcard(flashcards)
        context.update({"flashcard": flashcard, "show_answer": False})
        return context

    def post(self, request, *args, **kwargs):
        category = kwargs.get("category")
        flashcard_id = request.POST.get("flashcard_id")
        flashcard = get_object_or_404(Flashcard, id=flashcard_id)

        if "show_answer" in request.POST:
            context = {
                "flashcard": flashcard,
                "show_answer": True,
            }
            return render(request, self.template_name, context)

        correct = "correct" in request.POST
        flashcard.update_statistics(correct)
        return redirect("flashcards:learn_flashcards", category=category)


# ------------------------------------------------------------------
# 7) OCR RESULTS
# ------------------------------------------------------------------
class OCRResultsView(View):
    """
    Displays results of OCR processing.
    """

    template_name = "flashcards/ocr_results.html"

    def post(self, request, *args, **kwargs):
        if "image" not in request.FILES:
            messages.error(request, "No image file provided.")
            return redirect("flashcards:upload_photo")

        image = request.FILES["image"]
        category = request.POST.get("category", "default")

        try:
            flashcards = FlashcardFacade.generate_flashcards_from_image(image, category)

            # Store flashcards temporarily in session
            request.session["temp_flashcards"] = [
                {
                    "id": idx,
                    "question": fc.question,
                    "answer": fc.answer,
                    "category": category,
                }
                for idx, fc in enumerate(flashcards)
            ]
            logger.debug(
                f"Session flashcards set: {request.session['temp_flashcards']}"
            )

            extracted_text = "\n".join(fc.question for fc in flashcards)
            return render(
                request,
                self.template_name,
                {
                    "flashcards": request.session["temp_flashcards"],
                    "text": extracted_text,
                    "categories": GroupService.get_categories(),
                },
            )

        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
            messages.error(
                request, "An error occurred during OCR processing. Please try again."
            )
            return redirect("flashcards:upload_photo")


# ------------------------------------------------------------------
# 8) SAVE FLASHCARDS (bulk from session)
# ------------------------------------------------------------------
class SaveFlashcardsView(View):
    """
    Saves selected flashcards from the session.
    """

    def post(self, request, *args, **kwargs):
        temp_flashcards = request.session.get("temp_flashcards", [])
        selected_flashcard_ids = request.POST.getlist("flashcard_ids")

        logger.debug(f"Selected flashcard IDs: {selected_flashcard_ids}")
        logger.debug(f"Session flashcards: {temp_flashcards}")

        saved_count = 0
        for flashcard_data in temp_flashcards:
            if str(flashcard_data["id"]) in selected_flashcard_ids:
                question = request.POST.get(
                    f"question_{flashcard_data['id']}", ""
                ).strip()
                answer = request.POST.get(f"answer_{flashcard_data['id']}", "").strip()

                # 1) The existing-category dropdown
                category_select = request.POST.get(
                    f"category_select_{flashcard_data['id']}", ""
                ).strip()

                # 2) The text field for a new category
                category_new = request.POST.get(
                    f"category_new_{flashcard_data['id']}", ""
                ).strip()

                # Decide which category to use
                if category_new:
                    final_category = category_new
                elif category_select:
                    final_category = category_select
                else:
                    final_category = "default"

                if not question or not answer:
                    logger.warning(
                        f"Skipping flashcard ID {flashcard_data['id']} due to empty question or answer."
                    )
                    continue

                Flashcard.objects.create(
                    question=question,
                    answer=answer,
                    category=final_category,
                )
                saved_count += 1

        request.session.pop("temp_flashcards", None)
        messages.success(request, f"{saved_count} flashcards saved successfully.")
        return redirect("flashcards:flashcard_list")

    def get(self, request, *args, **kwargs):
        messages.error(request, "Invalid request method.")
        return redirect("flashcards:generate_from_text")


# ------------------------------------------------------------------
# 9) GENERATE FROM TEXT
# ------------------------------------------------------------------
class GenerateFromTextView(TemplateView):
    """
    Generates flashcards from user-entered text (NLP).
    """

    template_name = "flashcards/generate_from_text.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["flashcards"] = self.request.session.get("temp_flashcards", [])
        context["categories"] = GroupService.get_categories()
        return context

    def post(self, request, *args, **kwargs):
        text = request.POST.get("text", "").strip()
        if not text:
            messages.error(request, "The text field cannot be empty.")
            return render(request, self.template_name, {"flashcards": []})

        try:
            flashcard_objects = FlashcardFacade.generate_flashcards_from_text(text)
            flashcards_data = [
                {
                    "id": idx,
                    "question": fc.question,
                    "answer": fc.answer,
                    "category": fc.category or "default",
                }
                for idx, fc in enumerate(flashcard_objects)
            ]

            request.session["temp_flashcards"] = flashcards_data
            messages.success(
                request,
                f"Successfully generated {len(flashcards_data)} flashcards from the provided text.",
            )

            return render(
                request,
                self.template_name,
                {
                    "flashcards": flashcards_data,
                    "categories": GroupService.get_categories(),
                },
            )
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            messages.error(request, "An error occurred while generating flashcards.")
            return render(request, self.template_name, {"flashcards": []})


# ------------------------------------------------------------------
# 10) UPLOAD PHOTO
# ------------------------------------------------------------------
class UploadPhotoView(TemplateView):
    """
    Allows the user to upload a photo for OCR-based flashcard generation.
    """

    template_name = "flashcards/upload_photo.html"

    def post(self, request, *args, **kwargs):
        if "photo" not in request.FILES:
            messages.error(request, "No image file provided.")
            return render(request, self.template_name)

        photo = request.FILES["photo"]
        if not photo.content_type.startswith("image/"):
            messages.error(request, "The uploaded file is not an image.")
            return render(request, self.template_name)

        temp_folder = "temp"
        os.makedirs(temp_folder, exist_ok=True)
        file_path = os.path.join(temp_folder, photo.name)

        try:
            with open(file_path, "wb") as f:
                for chunk in photo.chunks():
                    f.write(chunk)

            flashcard_objects = FlashcardFacade.generate_flashcards_from_image(
                file_path
            )
            flashcards_data = [
                {
                    "id": idx,
                    "question": fc.question,
                    "answer": fc.answer,
                    "category": "default",
                }
                for idx, fc in enumerate(flashcard_objects)
            ]

            request.session["temp_flashcards"] = flashcards_data
            messages.success(
                request, f"Successfully generated {len(flashcards_data)} flashcards."
            )

            return render(
                request,
                "flashcards/ocr_results.html",
                {
                    "flashcards": flashcards_data,
                    "text": "Here you might display extracted OCR text",
                    "categories": GroupService.get_categories(),
                },
            )
        except Exception as e:
            logger.error(f"Error processing the image: {e}")
            messages.error(request, "An error occurred while processing the image.")

        return render(request, self.template_name)
