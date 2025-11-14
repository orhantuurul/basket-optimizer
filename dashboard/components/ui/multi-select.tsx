"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { Check, ChevronDown, X } from "lucide-react";
import {
  KeyboardEvent,
  MouseEvent,
  useCallback,
  useLayoutEffect,
  useMemo,
  useState,
} from "react";

export type Option = {
  label: string;
  value: string;
};

interface MultiSelectProps {
  options: Option[];
  values: string[];
  onValuesChange: (values: string[]) => void;
  className?: string;
  placeholder?: string;
}

export function MultiSelect({
  options,
  values,
  onValuesChange,
  className,
  placeholder = "Select items...",
}: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setSearch("");
    }
    setOpen(open);
  };

  const handleUnselect = useCallback(
    (value: string | number, event: MouseEvent | KeyboardEvent) => {
      event.preventDefault();
      event.stopPropagation();
      onValuesChange(values.filter((i) => i !== value));
    },
    [onValuesChange, values]
  );

  const handleSelectAll = () => {
    const newValues =
      values.length === options.length ? [] : options.map((opt) => opt.value);
    onValuesChange(newValues);
  };

  const filteredOptions = useMemo(
    () =>
      options.filter((option) =>
        option.label.toLowerCase().includes(search.toLowerCase())
      ),
    [options, search]
  );

  useLayoutEffect(() => {
    if (open) {
      const trigger = document.querySelector('[role="combobox"]');
      if (trigger) {
        const width = trigger.getBoundingClientRect().width;
        document.documentElement.style.setProperty(
          "--radix-popover-trigger-width",
          `${width}px`
        );
      }
    }
  }, [open]);

  return (
    <Popover open={open} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("h-auto w-full justify-between", className)}
        >
          <div className="flex max-h-[120px] flex-wrap items-center gap-1 overflow-y-auto">
            {values.length > 0 ? (
              values.map((value) => (
                <Badge
                  variant="secondary"
                  key={value}
                  className="max-w-[300px] truncate"
                >
                  <span className="truncate">
                    {options.find((option) => option.value === value)?.label}
                  </span>
                  <span
                    className="ml-1 shrink-0 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    onMouseDown={(event) => handleUnselect(value, event)}
                    onClick={(event) => handleUnselect(value, event)}
                  >
                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                  </span>
                </Badge>
              ))
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
          </div>
          <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        className="w-(--radix-popover-trigger-width) p-0"
        align="start"
      >
        <Command className={className}>
          <CommandInput placeholder="Search..." onValueChange={setSearch} />
          <CommandList>
            <CommandEmpty>No item found.</CommandEmpty>
            <CommandItem onSelect={handleSelectAll} className="border-b">
              <Check
                className={cn(
                  "mr-2 h-4 w-4",
                  values.length === options.length ? "opacity-100" : "opacity-0"
                )}
              />
              {values.length === options.length ? "Deselect All" : "Select All"}
            </CommandItem>
            <CommandGroup className="max-h-64 overflow-auto">
              {filteredOptions.map((option) => (
                <CommandItem
                  key={option.value}
                  onSelect={() => {
                    onValuesChange(
                      values.some((value) => value === option.value)
                        ? values.filter((value) => value !== option.value)
                        : [...values, option.value]
                    );
                    setOpen(true);
                  }}
                  className="truncate"
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      values.some((value) => value === option.value)
                        ? "opacity-100"
                        : "opacity-0"
                    )}
                  />
                  {option.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
