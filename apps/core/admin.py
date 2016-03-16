from django.contrib import admin

from .models import (BreedGroup, Breed, Animal, Owner, AnimalPedigreeNumber, AnimalTitle, AnimalOwner,
                     Kennel, AnimalKennel,
                     Show, ShowClass, ShowMember, ShowGroup,
                     ShowCatalog, ShowCatalogItem,
                     DocTemplate, DocTemplateElement)


class BreedGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(BreedGroup, BreedGroupAdmin)


class BreedAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'group')
    list_filter = ('group',)


admin.site.register(Breed, BreedAdmin)


class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'work')
    search_fields = ('name', 'address', 'phone', 'email')

admin.site.register(Owner, OwnerAdmin)


class KennelAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'breeder')
    search_fields = ('name', 'address', 'breeder')

admin.site.register(Kennel, KennelAdmin)


class AnimalOwnerInline(admin.TabularInline):
    model = AnimalOwner
    raw_id_fields = ('owner', )
    extra = 0


class AnimalKennelInline(admin.TabularInline):
    model = AnimalKennel
    raw_id_fields = ('kennel', )
    extra = 0


class AnimalPedigreeNumberInline(admin.TabularInline):
    model = AnimalPedigreeNumber
    extra = 0


class AnimalTitleInline(admin.TabularInline):
    model = AnimalTitle
    extra = 0


class AnimalAdmin(admin.ModelAdmin):
    search_fields = ('name_ru', 'name_en')
    list_display = ('get_display', 'breed', 'gender', 'get_color', 'birthdate', 'father', 'mother', 'reg_number',
                    'is_our')
    list_filter = ('gender', 'is_our', 'breed')
    inlines = (AnimalPedigreeNumberInline, AnimalTitleInline, AnimalOwnerInline, AnimalKennelInline)


admin.site.register(Animal, AnimalAdmin)


class ShowAdmin(admin.ModelAdmin):
    pass


admin.site.register(Show, ShowAdmin)


class ShowGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShowGroup, ShowGroupAdmin)


class ShowClassAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShowClass, ShowClassAdmin)


class ShowMemberAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'show', 'number')


admin.site.register(ShowMember, ShowMemberAdmin)


class ShowCatalogItemInline(admin.TabularInline):
    model = ShowCatalogItem
    extra = 0


class ShowCatalogAdmin(admin.ModelAdmin):
    inlines = (ShowCatalogItemInline,)


admin.site.register(ShowCatalog, ShowCatalogAdmin)


class DocTemplateElementInline(admin.TabularInline):
    model = DocTemplateElement
    extra = 0


class DocTemplateAdmin(admin.ModelAdmin):
    inlines = (DocTemplateElementInline,)


admin.site.register(DocTemplate, DocTemplateAdmin)
