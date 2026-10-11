from celery import shared_task
from quran.models import (
    RasmOlMushaf,
    Recitation,
    RecitationSurah,
    RecitationSurahTimestamp,
    Surah,
    SurahName,
    Ayah,
    Word,
    Translation,
    AyahTranslation,
    Transmission,
    WordText,
    RomSurahAyahs,
)
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from datetime import datetime, timedelta, timezone
import requests

from core.expressions import UUIDv7
from uuid import uuid7
from core.models import Notification


@shared_task(bind=True, serializer="json", name="forced-alignment-result")
def forced_alignment_result(self, words_timestamps):
    try:
        response = requests.get(words_timestamps, timeout=30)
        response.raise_for_status()
        payload = response.json()

        additional = payload.get("additional")
        if not additional:
            raise ValueError(
                "Additional data is not found in the downloaded words_timestamps data!"
            )

        recitation_uuid = additional.get("recitation_uuid")
        surah_uuid = additional.get("surah_uuid")
        file_s3_uuid = additional.get("file_s3_uuid")
        word_uuids = additional.get("word_uuids")
        user_id = additional.get("user_id")

        if not recitation_uuid or not surah_uuid:
            raise ValueError(
                "recitation_uuid and surah_uuid are required in additional"
            )

        # words_timestamps is now expected to be a URL returning JSON: { "results": [ ... ] }
        if not isinstance(words_timestamps, str):
            raise ValueError(
                "words_timestamps must be a URL string to the alignment results JSON"
            )

        # Extract list from { "results": [...] }
        words_timestamps_data = payload.get("results")
        if not isinstance(words_timestamps_data, list):
            raise ValueError(
                "Alignment results JSON must have a 'results' key with a list value"
            )

        try:
            recitation = Recitation.objects.get(uuid=recitation_uuid)
        except Recitation.DoesNotExist:
            raise ValueError(f"Recitation with uuid {recitation_uuid} not found")

        try:
            surah = Surah.objects.get(uuid=surah_uuid)
        except Surah.DoesNotExist:
            raise ValueError(f"Surah with uuid {surah_uuid} not found")

        file_obj = None
        if file_s3_uuid:
            from core.models import File

            try:
                file_obj = File.objects.get(s3_uuid=file_s3_uuid)
            except File.DoesNotExist:
                pass

        recitation_surah, created = RecitationSurah.objects.get_or_create(
            recitation=recitation,
            surah=surah,
            defaults={"file": file_obj} if file_obj else {},
        )

        if file_obj and not recitation_surah.file_id:
            recitation_surah.file = file_obj
            recitation_surah.save(update_fields=["file"])
        if word_uuids:
            words = list(
                Word.objects.filter(uuid__in=word_uuids).order_by("ayah__number", "id")
            )
        else:
            words = list(
                Word.objects.filter(ayah__surah=surah).order_by("ayah__number", "id")
            )

        if not words:
            raise ValueError(f"No words found for surah {surah_uuid}")

        word_idx = 0
        timestamp_objs = []

        with transaction.atomic():
            for word_data in words_timestamps_data:
                while word_idx < len(words) and words[word_idx].text != word_data.get(
                    "text"
                ):
                    word_idx += 1

                if word_idx < len(words):
                    word_obj = words[word_idx]
                    start_time = (
                        datetime.min + timedelta(seconds=word_data["start"])
                    ).time()
                    end_time = (
                        (datetime.min + timedelta(seconds=word_data["end"])).time()
                        if word_data.get("end")
                        else None
                    )

                    timestamp_objs.append(
                        RecitationSurahTimestamp(
                            recitation_surah=recitation_surah,
                            start_time=start_time,
                            end_time=end_time,
                            word=word_obj,
                        )
                    )
                    word_idx += 1

            if timestamp_objs:
                RecitationSurahTimestamp.objects.bulk_create(timestamp_objs)

        if user_id:
            try:
                User = get_user_model()
                user = User.objects.get(id=user_id)
                Notification.objects.create(
                    user=user,
                    resource_controller="recitations",
                    resource_action="",
                    resource_uuid=recitation.uuid,
                    status=Notification.STATUS_NOTHING,
                    description=f"Recitation timestamps generated",
                    message=f"Recitation timestamps generated for recitation {recitation.uuid}.",
                    message_type=Notification.MESSAGE_TYPE_SUCCESS,
                )
            except Exception:
                pass

        return f"Timestamps generated successfully for {len(timestamp_objs)} words"

    except Exception as e:
        if additional.get("user_id"):
            try:
                User = get_user_model()
                user = User.objects.get(id=additional["user_id"])
                recitation_uuid = additional.get("recitation_uuid", "unknown")
                Notification.objects.create(
                    user=user,
                    resource_controller="quran.tasks.forced_alignment_result",
                    resource_action="",
                    resource_uuid=(
                        recitation_uuid if isinstance(recitation_uuid, str) else None
                    ),
                    status=Notification.STATUS_NOTHING,
                    description=f"Failed to generate recitation timestamps",
                    message=f"Failed to generate recitation timestamps: {str(e)}",
                    message_type=Notification.MESSAGE_TYPE_FAILED,
                )
            except Exception:
                pass

        return f"Failed to generate timestamps: {str(e)}"


@shared_task(bind=True, serializer="json")
def forced_alignment(self, audio_url, text, additional):
    task_info = {
        "task_id": self.request.id,
        "input_data": {
            "mp3_url": audio_url,
            "text": text,
            "additional": additional,
        },
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task_type": "forcedalignment_processing",
    }

    return {
        "status": "queued",
        "task_id": self.request.id,
        "message": "Task queued for Forced alignment processing",
    }


@shared_task
def import_mushaf_task(quran_data, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    mushaf_data = quran_data["mushaf"]
    compiler = None
    published = "published" if mushaf_data["published"] is True else "draft"
    try:
        if mushaf_data["compiler_name"]:
            compiler, created = User.objects.get_or_create(
                username=mushaf_data["compiler_name"]
            )
        with transaction.atomic():
            mushaf = RasmOlMushaf.objects.create(
                creator_id=user.id,
                name=mushaf_data["name"],
                slug=mushaf_data["slug"],
                compiler=compiler,
                status=published,
            )
            transmission = Transmission.objects.create(
                creator_id=user.id,
                rasm_ol_mushaf=mushaf,
                slug=mushaf_data["transmission"]["slug"],
                name=mushaf_data["transmission"]["name"],
            )
            surah_objs = []
            for surah_data in quran_data["surahs"]:
                s = Surah(
                    creator_id=user.id,
                    number=surah_data["number"],
                    # name=surah_data["name"],
                    has_bismillah=surah_data["has_bismillah"],
                    bismillah_text=surah_data["bismillah_text"],
                    period=surah_data["period"],
                )
                surah_objs.append(s)
            Surah.objects.bulk_create(surah_objs)
            surahs_by_number = {s.number: s for s in surah_objs}
            
            surah_name_objs = []
            for surah_data in quran_data["surahs"]:
                name_value = surah_data.get("name", "")[:50]
                if not name_value:
                    continue
                surah_name_objs.append(
                    SurahName(
                        surah=surahs_by_number[surah_data["number"]],
                        name=name_value,
                    )
                )
            if surah_name_objs:
                SurahName.objects.bulk_create(surah_name_objs)

            ayah_objs = []
            for surah_data in quran_data["surahs"]:
                surah = surahs_by_number[surah_data["number"]]
                for ayah in surah_data["ayahs"]:
                    # Calculate length from words if available
                    length = 0
                    if "words" in ayah:
                        text = " ".join(word["text"] for word in ayah["words"])
                        length = len(text)

                    a = Ayah(
                        id=uuid7(),
                        creator_id=user.id,
                        surah=surah,
                        number=ayah["number"],
                        sajdah=ayah["sajdah"],
                        is_bismillah=ayah["is_bismillah"],
                        length=length,
                    )
                    ayah_objs.append(a)
                    RomSurahAyahs.objects.create(
                        rasm_ol_mushaf=mushaf,
                        surah=surah,
                        ayah_id=a.id,
                        creator_id=user.id,
                    )

            Ayah.objects.bulk_create(ayah_objs)
            ayahs_by_surah_and_number = {(a.surah.number, a.number): a for a in ayah_objs}
            word_objs = []
            word_texts = []
            for surah_data in quran_data["surahs"]:
                for ayah in surah_data["ayahs"]:
                    ayah_obj = ayahs_by_surah_and_number[
                        (surah_data["number"], ayah["number"])
                    ]
                    for word in ayah["words"]:
                        # Generating the id in the runtime of the api
                        # We need the ID in memory.
                        w = Word(id=uuid7(), ayah=ayah_obj, creator_id=user.id)
                        word_objs.append(w)
                        word_texts.append(
                            WordText(
                                text=word["text"],
                                # Need it here
                                word_id=w.id,
                                creator_id=user.id,
                                transmission=transmission,
                            )
                        )
            # Then here we insert to DB with no problem :)
            Word.objects.bulk_create(word_objs)
            WordText.objects.bulk_create(word_texts)
        # Send notification to user
        Notification.objects.create(
            user=user,
            resource_controller="mushafs",
            resource_action="import",
            resource_uuid=mushaf.id,
            status=Notification.STATUS_NOTHING,
            description=f"Mushaf import complete",
            message=f'Mushaf "{mushaf.name}" imported successfully.',
            message_type=Notification.MESSAGE_TYPE_SUCCESS,
        )
    except Exception as e:
        Notification.objects.create(
            user=user,
            resource_controller="quran.tasks.import_mushaf_task",
            resource_action="",
            resource_uuid=(
            ),
            status=Notification.STATUS_NOTHING,
            description=f"Failed to import mushaf",
            message=f"{e}", # TODO: Maybe Dont send every detail
            message_type=Notification.MESSAGE_TYPE_FAILED,
        )
    return f"Mushaf imported."


@shared_task
def import_translation_task(translation_data, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    try:
        with transaction.atomic():
        translator, _ = User.objects.get_or_create(
            username=translation_data["translator_username"]
        )
        rom = RasmOlMushaf.objects.get(slug=translation_data["rasm_ol_mushaf"])
        # Create new transmission for translation
        transmission = Transmission.objects.create(
            creator_id = user.id,
            rasm_ol_mushaf=rom,
            slug=f"translation-{translation_data["translator_username"]}-{translation_data["language"]}",
        )
        translation = Translation.objects.create(
            creator_id=user.id,
            transmission=transmission,
            translator_id=translator.id,
            source=translation_data["source"],
            status="published",
            language=translation_data["language"],
        )
        # Build a lookup for Ayah objects of this mushaf keyed by (surah_number, ayah_number)
        ayah_lookup = {
            (a.surah.number, a.number): a.id
            for a in Ayah.objects.filter(surah__rom_surah_ayahs_surah__rasm_ol_mushaf=rom)
            .only("id", "number", "surah__number")
            .select_related("surah")
        }

        ayah_translations = []
        # Root-level bismillah text (if provided) – used as default for all ayahs
        default_bismillah = translation_data.get("bismillah_text")

        for surah_data in translation_data["surahs"]:
            surah_number = surah_data["number"]
            for ayah_data in surah_data["ayah_translations"]:
                ayah_number = ayah_data["number"]
                ayah_id = ayah_lookup.get((surah_number, ayah_number))
                if ayah_id is None:
                    # Skip if corresponding ayah not found (data mismatch)
                    continue
                ayah_translations.append(
                    AyahTranslation(
                        creator_id=user.id,
                        translation_id=translation.id,
                        ayah_id=ayah_id,
                        text=ayah_data["text"],
                        bismillah=ayah_data.get("bismillah_text") or default_bismillah,
                    )
                )
        AyahTranslation.objects.bulk_create(ayah_translations)
        Notification.objects.create(
            user=user,
            resource_controller="translations",
            resource_action="import",
            resource_uuid=translation.id,
            status=Notification.STATUS_NOTHING,
            description=f"Translation import complete",
            message=f"Translation {translation.id} imported successfully.",
            message_type=Notification.MESSAGE_TYPE_SUCCESS,
        )
    except Exception:
        Notification.objects.create(
            user=user,
            resource_controller="quran.tasks.import_translation_task",
            resource_action="",
            resource_uuid=(
            ),
            status=Notification.STATUS_NOTHING,
            description=f"Failed to import Translation",
            message=f"{e}", # TODO: Maybe Dont send every detail
            message_type=Notification.MESSAGE_TYPE_FAILED,
        )
    return f"Translation {translation.id} imported successfully."
